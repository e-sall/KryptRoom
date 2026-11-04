from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class GovernanceRevisionRef:
    """Metadata reference only. Never a StatePolicy, consent signature or execution grant."""

    room_id: UUID
    revision_id: UUID


class GovernanceReader(Protocol):
    def current_revision(self, room_id: UUID) -> GovernanceRevisionRef | None: ...
