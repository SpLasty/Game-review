"""Optional extraction-provider seam for genuinely ambiguous prose.

The default Stage 2 run is deterministic and makes no network/model calls. A future
provider can implement this protocol; all returned offsets are validated against the
exact source text before any row is accepted.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ProposedChange:
    source_start: int
    source_end: int
    entity: str | None
    aspect: str | None
    action: str | None
    direction: str | None
    developer_status: str
    confidence: float


class ChangeExtractionProvider(Protocol):
    """Provider contract; implementations should use structured output/schema mode."""

    def extract_changes(self, *, game_name: str, source_text: str) -> list[ProposedChange]:
        """Return exact character offsets into source_text, without paraphrasing spans."""


def validate_proposal(source_text: str, proposal: ProposedChange) -> tuple[bool, str | None]:
    """Reject unverifiable, out-of-bounds, or malformed model-proposed spans."""
    if not (0 <= proposal.source_start < proposal.source_end <= len(source_text)):
        return False, "offset_out_of_bounds"
    if not source_text[proposal.source_start : proposal.source_end].strip():
        return False, "empty_source_span"
    if not 0.0 <= proposal.confidence <= 1.0:
        return False, "confidence_out_of_range"
    if proposal.developer_status not in {
        "implemented_change",
        "implemented_bug_fix",
        "acknowledged_or_planned",
        "unclear",
    }:
        return False, "invalid_developer_status"
    return True, None
