"""Small, transparent BM25 implementation for per-patch claim retrieval."""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable

TOKEN_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", flags=re.UNICODE)
STOP_WORDS = frozenset(
    "a an and are as at be been but by can did do does for from had has have he her hers "
    "him his i if in into is it its me my of on or our ours she so than that the their "
    "them then there these they this those to us was we were what when where which who "
    "will with you your yours recommend recommended recommendation review game games "
    "good great bad awful terrible poor love loved hate hated like liked dislike "
    "broken unbalanced sucks awesome amazing worst best fine fun enjoyable "
    "not no never really just very still now update patch after before".split()
)


def tokenize(text: str | None) -> list[str]:
    """Return normalized content tokens, retaining entities and numeric values."""
    if not text:
        return []
    return [
        token.casefold()
        for token in TOKEN_RE.findall(text)
        if token.casefold() not in STOP_WORDS and len(token) > 1
    ]


def change_query_text(change: dict) -> str:
    """Build a query from the atomic change plus its local hierarchy."""
    parts = [
        change.get("change_text"),
        change.get("entity"),
        change.get("aspect"),
        change.get("action"),
        change.get("direction"),
        " ".join(change.get("heading_path") or []),
    ]
    return " ".join(str(part) for part in parts if part)


def claim_document_text(claim: dict) -> str:
    """Use claim content and Stage 2 structured terms, excluding vote sentiment."""
    parts = [claim.get("claim_text_original"), claim.get("referenced_entity"), claim.get("aspect")]
    return " ".join(str(part) for part in parts if part)


@dataclass(frozen=True)
class RankedHit:
    item_id: str
    rank: int
    score: float


class BM25Index:
    """Okapi BM25 index whose scores are calculated only for shared content tokens."""

    def __init__(
        self,
        documents: Iterable[tuple[str, str]],
        *,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        rows = list(documents)
        self.ids = [doc_id for doc_id, _ in rows]
        self.k1 = k1
        self.b = b
        self.tokens = [tokenize(text) for _, text in rows]
        self.lengths = [len(tokens) for tokens in self.tokens]
        self.average_length = sum(self.lengths) / len(self.lengths) if self.lengths else 0.0
        self.postings: dict[str, list[tuple[int, int]]] = defaultdict(list)
        document_frequency: Counter[str] = Counter()
        for index, tokens in enumerate(self.tokens):
            frequencies = Counter(tokens)
            for token, frequency in frequencies.items():
                self.postings[token].append((index, frequency))
                document_frequency[token] += 1
        self.document_count = len(rows)
        self.idf = {
            token: math.log1p((self.document_count - frequency + 0.5) / (frequency + 0.5))
            for token, frequency in document_frequency.items()
        }

    def rank(self, query: str, *, limit: int | None) -> list[RankedHit]:
        if limit is not None and limit < 1:
            raise ValueError("BM25 limit must be positive")
        query_terms = set(tokenize(query))
        if not query_terms or not self.document_count:
            return []
        scores: dict[int, float] = defaultdict(float)
        for term in query_terms:
            for doc_index, frequency in self.postings.get(term, ()):
                length = self.lengths[doc_index]
                denominator = frequency + self.k1 * (
                    1.0 - self.b + self.b * length / (self.average_length or 1.0)
                )
                scores[doc_index] += self.idf[term] * frequency * (self.k1 + 1.0) / denominator
        ordered = sorted(
            ((self.ids[index], score) for index, score in scores.items() if score > 0),
            key=lambda hit: (-hit[1], hit[0]),
        )
        if limit is not None:
            ordered = ordered[:limit]
        return [
            RankedHit(item_id, rank, float(score))
            for rank, (item_id, score) in enumerate(ordered, 1)
        ]
