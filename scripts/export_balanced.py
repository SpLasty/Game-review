# Saves an evenly capped set of reviews for each game.

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def capped(rows, cap, minimum=None):
    counts = Counter()
    selected = []
    for row in sorted(rows, key=lambda r: (int(r['timestamp_created']), int(r['review_id']), -int(r['appid'])), reverse=True):
        if minimum is not None and int(row['word_count']) < minimum:
            continue
        appid = int(row['appid'])
        if counts[appid] < cap:
            selected.append(row)
            counts[appid] += 1
    return selected


def write_csv(path, rows, fields):
    path = Path(path)
    temp = path.with_suffix('.tmp')
    try:
        with temp.open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def export(snapshot, out, cap, minimum):
    manifest = json.loads((snapshot / 'manifest.json').read_text(encoding='utf-8'))
    configured = json.loads((ROOT / 'data/games.json').read_text(encoding='utf-8'))

    if (snapshot / 'game_catalog.json').exists():
        configured = json.loads((snapshot / 'game_catalog.json').read_text(encoding='utf-8'))
    with (out / 'all_english_reviews.csv').open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)
    assert len({(r['appid'], r['review_id']) for r in rows}) == len(rows)
    raw = capped(rows, cap)
    text = capped(rows, cap, minimum)
    unedited = [r for r in text if r['unedited'] == 'True']
    write_csv(out / 'balanced_reviews.csv', text, fields)
    summaries = []
    for key, name in configured.items():
        appid = int(key)
        group = [r for r in rows if int(r['appid']) == appid]
        rg = [r for r in raw if int(r['appid']) == appid]
        tg = [r for r in text if int(r['appid']) == appid]
        ug = [r for r in unedited if int(r['appid']) == appid]
        summaries.append(dict(appid=appid, game=name, raw_saved=len(group),
            eligible_saved=sum(int(r['word_count']) >= minimum for r in group),
            raw_selected=len(rg), text_selected=len(tg), text_unedited=len(ug),
            raw_negative=sum(r['recommended'] == 'False' for r in rg),
            text_negative=sum(r['recommended'] == 'False' for r in tg),
            raw_oldest_utc=min((r['created_utc'] for r in rg), default=''),
            raw_newest_utc=max((r['created_utc'] for r in rg), default=''),
            text_oldest_utc=min((r['created_utc'] for r in tg), default=''),
            text_newest_utc=max((r['created_utc'] for r in tg), default=''),
            cap=cap, minimum_words=minimum,
            status='cap_met' if len(rg) == cap and len(tg) == cap else 'shortfall'))
    assert all(s['text_selected'] <= cap for s in summaries)
    assert len(text) == sum(s['text_selected'] for s in summaries)
    assert all(int(r['word_count']) >= minimum for r in text)
    assert all(r['unedited'] == 'True' for r in unedited)
    result = dict(snapshot=manifest['snapshot'], exported_utc=datetime.now(timezone.utc).isoformat(),
        cap_per_game=cap, minimum_words=minimum, configured_games=len(configured),
        games_meeting_cap=sum(s['status'] == 'cap_met' for s in summaries),
        raw_saved=len(rows), raw_downloaded=sum(g['raw_reviews'] for g in manifest['games']), raw_balanced=len(raw), text_balanced=len(text),
        excluded_language_reviews=sum(g['raw_reviews'] for g in manifest['games'])-len(rows),
        text_balanced_unedited=len(unedited), games=summaries,
        selection='Most recent creation timestamp first; review ID breaks ties. No sentiment quota.',
        short_review_policy='All short English reviews remain in all_english_reviews.csv; the word count and text_eligible columns identify them.',
        limitations=['Equal game counts do not make a sample representative of Steam.',
            'The raw and text selections cover different dates and contain different reviews.',
            'Unedited text is a subset of the capped text set, so its game counts can differ.',
            'Game selection is purposive and has no probability sampling frame.'],
        sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('reviews_balanced*.csv')})
    (out / 'balanced_manifest.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['configured_games', 'games_meeting_cap', 'raw_saved', 'raw_balanced', 'text_balanced', 'text_balanced_unedited']}, indent=2))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', default='raw/steam_30_games')
    parser.add_argument('--output-dir', default='data/processed/steam_30_games')
    parser.add_argument('--cap', type=int, default=1000)
    parser.add_argument('--min-words', type=int, default=10)
    args = parser.parse_args()
    if args.cap < 1 or args.min_words < 1:
        parser.error('Cap and word minimum must be positive')
    export(ROOT / 'data' / args.snapshot, ROOT / args.output_dir, args.cap, args.min_words)
