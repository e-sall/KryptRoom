from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class InvitationTarget:
    """Pre-registered organization reference; no bearer token, acceptance or grant in PR1."""

    room_id: UUID
    organization_id: UUID
