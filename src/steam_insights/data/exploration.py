"""Aggregate-only exploratory artifacts; no review text is copied into reports."""

import os

import pandas as pd

from steam_insights.config import DataConfig
from steam_insights.data.io import inventory, read_csv, write_json
from steam_insights.data.preprocessing import word_count
from steam_insights.data.validation import (
    boolean_values,
    utc_dates,
    validate_announcements,
    validate_reviews,
)


def review_summary(frame: pd.DataFrame, name: str, minimum_words: int) -> dict:
    votes = boolean_values(frame["recommended"])
    created = utc_dates(frame["created_utc"])
    updated = utc_dates(frame["updated_utc"])
    counts = frame["review_text"].fillna("").map(word_count)
    return {
        "dataset": name,
        "reviews": len(frame),
        "games": int(frame["appid"].nunique()),
        "negative_votes": int(votes.eq(False).sum()),
        "valid_votes": int(votes.notna().sum()),
        "negative_share": float(votes.eq(False).sum() / votes.notna().sum())
        if votes.notna().any()
        else None,
        "minimum_words": minimum_words,
        "below_minimum_words": int(counts.lt(minimum_words).sum()),
        "edited_latest_snapshot": int(
            (created.notna() & updated.notna() & created.ne(updated)).sum()
        ),
        "earliest_created_utc": created.min().isoformat() if created.notna().any() else None,
        "latest_created_utc": created.max().isoformat() if created.notna().any() else None,
    }


def _review_tables(
    frame: pd.DataFrame, minimum_words: int
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    work = frame[["appid", "game"]].copy()
    work["created"] = utc_dates(frame["created_utc"])
    work["updated"] = utc_dates(frame["updated_utc"])
    votes = boolean_values(frame["recommended"])
    work["negative"] = votes.eq(False).fillna(False).astype("int64")
    work["valid_vote"] = votes.notna().astype("int64")
    work["words"] = frame["review_text"].fillna("").map(word_count)
    work["short"] = work["words"].lt(minimum_words).astype("int64")
    work["edited"] = (
        work["created"].notna() & work["updated"].notna() & work["created"].ne(work["updated"])
    ).astype("int64")
    per_game = (
        work.groupby(["appid", "game"], sort=True)
        .agg(
            reviews=("appid", "size"),
            negative_votes=("negative", "sum"),
            valid_votes=("valid_vote", "sum"),
            short_reviews=("short", "sum"),
            edited_reviews=("edited", "sum"),
            earliest_created_utc=("created", "min"),
            latest_created_utc=("created", "max"),
        )
        .reset_index()
    )
    per_game["negative_share"] = per_game["negative_votes"] / per_game["valid_votes"].replace(
        0, float("nan")
    )
    work["date_utc"] = work["created"].dt.floor("D")
    daily = (
        work.groupby(["appid", "game", "date_utc"], sort=True)
        .agg(
            reviews=("appid", "size"),
            negative_votes=("negative", "sum"),
            valid_votes=("valid_vote", "sum"),
        )
        .reset_index()
    )
    daily["negative_share"] = daily["negative_votes"] / daily["valid_votes"].replace(
        0, float("nan")
    )
    # Extremes are potentially partial days; dates alone do not prove contiguous source coverage.
    bounds = work.groupby("appid")["date_utc"].agg(["min", "max"])
    daily["boundary_day"] = [
        date in (bounds.loc[app, "min"], bounds.loc[app, "max"])
        for app, date in zip(daily["appid"], daily["date_utc"])
    ]
    bins = [-1, 0, 4, 9, 19, 49, 99, float("inf")]
    work["word_bin"] = pd.cut(
        work["words"], bins=bins, labels=["0", "1-4", "5-9", "10-19", "20-49", "50-99", "100+"]
    )
    lengths = (
        work.groupby("word_bin", observed=False)
        .agg(
            reviews=("words", "size"),
            negative_votes=("negative", "sum"),
            valid_votes=("valid_vote", "sum"),
        )
        .reset_index()
    )
    lengths["negative_share"] = lengths["negative_votes"] / lengths["valid_votes"].replace(
        0, float("nan")
    )
    return per_game, daily, lengths


def _plots(
    config: DataConfig,
    per_game: pd.DataFrame,
    daily: pd.DataFrame,
    lengths: pd.DataFrame,
    comparison: pd.DataFrame,
) -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(config.root / ".matplotlib"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plots = config.reports_dir / "figures"
    plots.mkdir(exist_ok=True)
    ordered = per_game.sort_values("reviews")
    fig, ax = plt.subplots(figsize=(10, 9))
    ax.barh(ordered["game"], ordered["reviews"], color="#247B8A")
    ax.set(
        xlabel="Collected reviews (not total Steam population)",
        title="Source snapshot volume by game",
    )
    fig.tight_layout()
    fig.savefig(plots / "reviews_by_game.png", dpi=150)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(lengths["word_bin"].astype(str), lengths["reviews"], color="#247B8A")
    ax.set(
        xlabel="Unicode word runs",
        ylabel="Reviews",
        title="Review length: all collected English reviews",
    )
    fig.tight_layout()
    fig.savefig(plots / "review_lengths.png", dpi=150)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(comparison["dataset"], comparison["negative_share"] * 100, color=["#247B8A", "#DA9155"])
    ax.set(
        ylabel="Negative recommendation (%)",
        title="Sampling sensitivity: different review populations",
    )
    fig.tight_layout()
    fig.savefig(plots / "recommendation_comparison.png", dpi=150)
    plt.close(fig)
    heatmap = daily.pivot(index="game", columns="date_utc", values="reviews").fillna(0)
    # Include zero-observation dates; the display must not compress missing calendar days.
    dates = pd.date_range(daily["date_utc"].min(), daily["date_utc"].max(), freq="D", tz="UTC")
    heatmap = heatmap.reindex(columns=dates, fill_value=0)
    fig, ax = plt.subplots(figsize=(12, 8))
    image = ax.imshow(
        heatmap.to_numpy(dtype=float, na_value=0),
        aspect="auto",
        interpolation="nearest",
        cmap="Blues",
    )
    ax.set_yticks(range(len(heatmap)), labels=heatmap.index)
    ticks = list(range(0, len(dates), max(1, len(dates) // 8)))
    ax.set_xticks(
        ticks, labels=[dates[i].strftime("%Y-%m-%d") for i in ticks], rotation=30, ha="right"
    )
    ax.set_title("Observed review counts by game/day; zero is not proof of source completeness")
    fig.colorbar(image, ax=ax, label="Collected reviews")
    fig.tight_layout()
    fig.savefig(plots / "coverage_by_game_day.png", dpi=150)
    plt.close(fig)


def profile(config: DataConfig) -> dict:
    frames = {
        kind: read_csv(config.source(kind)) for kind in ("reviews", "balanced", "announcements")
    }
    validations = [
        validate_reviews(frames[kind], kind, config.language) for kind in ("reviews", "balanced")
    ]
    validations.append(validate_announcements(frames["announcements"]))
    result = inventory(config)
    result["validation"] = [report.to_dict() for report in validations]
    notes_source = frames["announcements"]
    result["announcements"] = {
        "posts": len(notes_source),
        "games": int(notes_source["appid"].nunique()) if "appid" in notes_source else None,
        "heuristic_patch_candidates": int(boolean_values(notes_source["patch_candidate"]).sum())
        if "patch_candidate" in notes_source
        else None,
        "verification_flags": notes_source["verification_status"].value_counts().to_dict()
        if "verification_status" in notes_source
        else {},
        "branch_hints": notes_source["release_branch_hint"].value_counts().to_dict()
        if "release_branch_hint" in notes_source
        else {},
    }
    result["review_populations"] = [
        review_summary(frames[kind], kind, config.minimum_words)
        for kind in ("reviews", "balanced")
        if {"recommended", "appid", "review_text", "created_utc", "updated_utc"}.issubset(
            frames[kind]
        )
    ]
    config.reports_dir.mkdir(parents=True, exist_ok=True)
    write_json(config.reports_dir / "profile.json", result)
    # Persist diagnostics even if a missing required column prevents meaningful aggregate plots.
    if any(
        issue["check"] == "missing_columns" for report in validations for issue in report.issues
    ):
        _write_report(config, result)
        return result
    comparison = pd.DataFrame(result["review_populations"])
    comparison.to_csv(config.reports_dir / "population_comparison.csv", index=False)
    per_game, daily, lengths = _review_tables(frames["reviews"], config.minimum_words)
    per_game.to_csv(config.reports_dir / "reviews_by_game.csv", index=False)
    daily.to_csv(config.reports_dir / "reviews_by_day.csv", index=False)
    lengths.to_csv(config.reports_dir / "review_lengths.csv", index=False)
    missing = []
    for name, frame in frames.items():
        for column in frame:
            absent = frame[column].isna() | frame[column].str.strip().eq("")
            missing.append(
                {
                    "dataset": name,
                    "column": column,
                    "missing": int(absent.sum()),
                    "rows": len(frame),
                }
            )
    pd.DataFrame(missing).to_csv(config.reports_dir / "missing_values.csv", index=False)
    notes = frames["announcements"].copy()
    notes["date_utc"] = utc_dates(notes["date_utc"])
    notes.groupby(["appid", "game"]).agg(
        announcements=("gid", "size"),
        earliest_announcement_utc=("date_utc", "min"),
        latest_announcement_utc=("date_utc", "max"),
    ).reset_index().to_csv(config.reports_dir / "announcements_by_game.csv", index=False)
    if not daily.empty:
        _plots(config, per_game, daily, lengths, comparison)
    _write_report(config, result)
    return result


def _write_report(config: DataConfig, result: dict) -> None:
    lines = ["# Initial Steam data exploration", "", "## Review populations", ""]
    for item in result["review_populations"]:
        share = (
            f"{item['negative_share']:.2%}" if item["negative_share"] is not None else "unavailable"
        )
        lines.append(
            f"- **{item['dataset']}**: {item['reviews']:,} reviews; {share} negative votes "
            f"out of {item['valid_votes']:,} valid votes; "
            f"{item['below_minimum_words']:,} below {config.minimum_words} words."
        )
    lines += ["", "## Validation", ""]
    for item in result["validation"]:
        lines.append(f"- **{item['dataset']}**: {'passed' if item['valid'] else 'failed'}")
        lines.extend(
            f"  - {issue['severity']}: {issue['check']} ({issue['count']:,}) — {issue['detail']}"
            for issue in item["issues"]
        )
    lines += [
        "",
        "## Interpretation limits",
        "",
        "- The balanced file overlaps the full file: never concatenate them as new reviews.",
        "- A negative recommendation is not sentiment toward every patch change.",
        "- Short reviews remain in recommendation statistics; text filtering changes the population.",
        "- Coverage tables describe observed dates, not a proof that a patch window is complete.",
        "- Edited text and votes are the latest exported state, not their original historical values.",
        "- Patch/keyword flags are heuristics; no gold labels or causal patch effects are produced.",
        "- Original announcement heading markup is absent from these CSVs.",
        "",
        "See profile.json for source fingerprints and validation details, CSV tables for aggregate "
        "inspection, and figures/ for plots.",
        "",
    ]
    (config.reports_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")
