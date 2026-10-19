"""Game-scoped entity alias and aspect retrieval."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from steam_patch_relevance.stage3.bm25 import RankedHit

WORD_RE = re.compile(r"[^\W_]+", flags=re.UNICODE)
ASPECT_FAMILIES = {
    "price": "economy_cost",
    "cost": "economy_cost",
    "purchase price": "economy_cost",
    "economy": "economy_cost",
    "damage": "damage_output",
    "damage output": "damage_output",
    "dps": "damage_output",
    "health": "durability",
    "hp": "durability",
    "armor": "durability",
    "survivability": "durability",
    "cooldown": "cooldown_timing",
    "recharge": "cooldown_timing",
    "fire rate": "fire_rate",
    "attack speed": "fire_rate",
    "movement speed": "movement",
    "move speed": "movement",
    "movement": "movement",
    "crash": "stability",
    "stability": "stability",
    "performance": "performance",
    "frame rate": "performance",
    "fps": "performance",
    "lag": "networking",
    "network": "networking",
    "connectivity": "networking",
    "latency": "networking",
    "matchmaking": "matchmaking",
    "queue": "matchmaking",
    "progression": "progression_rewards",
    "experience": "progression_rewards",
    "xp": "progression_rewards",
    "reward": "progression_rewards",
    "rewards": "progression_rewards",
}


def normalize_term(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(WORD_RE.findall(value.casefold()))


class GameVocabulary:
    """Resolve aliases within one Steam game; aliases never cross app IDs."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.aliases: dict[str, set[str]] = defaultdict(set)
        self.alias_source: dict[str, set[str]] = defaultdict(set)
        for row in rows:
            if not row.get("is_entity_matchable", True):
                continue
            canonical = normalize_term(row.get("term") or row.get("normalized_term"))
            if not canonical:
                continue
            for alias in [row.get("term"), row.get("normalized_term"), *(row.get("aliases") or [])]:
                norm = normalize_term(alias)
                if norm:
                    self.aliases[norm].add(canonical)
                    self.alias_source[norm].add(str(alias))
        self._patterns = sorted(self.aliases, key=lambda value: (-len(value), value))
        alternatives = [
            r"(?<!\w)" + r"[\W_]+".join(re.escape(token) for token in alias.split()) + r"(?!\w)"
            for alias in self._patterns
        ]
        self._compiled = (
            re.compile("(?:" + "|".join(alternatives) + ")", re.IGNORECASE)
            if alternatives
            else None
        )

    def resolve(self, value: str | None) -> set[str]:
        norm = normalize_term(value)
        if not norm:
            return set()
        return set(self.aliases.get(norm, {norm}))

    def mentioned_entities(self, text: str | None) -> set[str]:
        aliases = self.mentioned_aliases(text)
        entities: set[str] = set()
        for alias in aliases:
            entities.update(self.aliases[alias])
        return entities

    def mentioned_aliases(self, text: str | None) -> set[str]:
        if not text:
            return set()
        aliases: set[str] = set()
        for match in self._compiled.finditer(text) if self._compiled is not None else ():
            alias = normalize_term(match.group(0))
            if alias in self.aliases:
                aliases.add(alias)
        return aliases

    def entity_set(self, row: dict[str, Any], *, change: bool) -> set[str]:
        fields = (
            [row.get("entity"), *(row.get("entity_candidates") or [])]
            if change
            else [row.get("referenced_entity")]
        )
        entities: set[str] = set()
        for field in fields:
            entities.update(self.resolve(field))
        text_fields = (
            [row.get("change_text"), " ".join(row.get("heading_path") or [])]
            if change
            else [row.get("claim_text_original")]
        )
        for text in text_fields:
            entities.update(self.mentioned_entities(str(text) if text else None))
        return entities


def aspect_family(value: str | None) -> str:
    normalized = normalize_term(value)
    return ASPECT_FAMILIES.get(normalized, normalized)


def _entity_strength(
    change_entities: set[str], claim_entities: set[str], vocabulary: GameVocabulary
) -> tuple[float, str | None]:
    shared = change_entities & claim_entities
    if not shared:
        return 0.0, None
    # Exact canonical mention ranks above a term/alias resolution, without discarding either.
    exact = sorted(
        shared & change_entities & claim_entities,
        key=lambda term: (-len(term), term),
    )
    if exact:
        return 1.0, exact[0]
    return 0.75, sorted(shared)[0]


def entity_aspect_score(
    change: dict[str, Any],
    claim: dict[str, Any],
    vocabulary: GameVocabulary,
    *,
    change_entities: set[str] | None = None,
    claim_entities: set[str] | None = None,
) -> tuple[float, float, float, str | None]:
    if change_entities is None:
        change_entities = vocabulary.entity_set(change, change=True)
    if claim_entities is None:
        claim_entities = vocabulary.entity_set(claim, change=False)
    entity_score, entity_match = _entity_strength(change_entities, claim_entities, vocabulary)
    change_aspect = aspect_family(change.get("aspect"))
    claim_aspect = aspect_family(claim.get("aspect"))
    aspect_score = float(bool(change_aspect and claim_aspect and change_aspect == claim_aspect))
    score = (2.0 * entity_score) + aspect_score
    return score, entity_score, aspect_score, entity_match


def rank_entity_aspect(
    change: dict[str, Any],
    claims: list[dict[str, Any]],
    vocabulary: GameVocabulary,
    *,
    limit: int | None,
    change_entities: set[str] | None = None,
    claim_entities_by_id: dict[str, set[str]] | None = None,
) -> list[tuple[RankedHit, float, float, str | None]]:
    if change_entities is None:
        change_entities = vocabulary.entity_set(change, change=True)
    hits = []
    for claim in claims:
        score, entity_score, aspect_score, matched_entity = entity_aspect_score(
            change,
            claim,
            vocabulary,
            change_entities=change_entities,
            claim_entities=(
                claim_entities_by_id.get(claim["claim_id"])
                if claim_entities_by_id is not None
                else None
            ),
        )
        if score > 0:
            hits.append((claim["claim_id"], score, entity_score, aspect_score, matched_entity))
    hits.sort(key=lambda row: (-row[1], row[0]))
    return [
        (RankedHit(item_id, rank, score), entity_score, aspect_score, matched_entity)
        for rank, (item_id, score, entity_score, aspect_score, matched_entity) in enumerate(
            hits[:limit] if limit is not None else hits, 1
        )
    ]
