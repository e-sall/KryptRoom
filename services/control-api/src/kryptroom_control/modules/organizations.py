from typing import Protocol
from uuid import UUID


class OrganizationDirectory(Protocol):
    """Controlled pilot enrollment; an email domain or token claim is not membership."""

    def is_active_member(self, organization_id: UUID, user_id: UUID) -> bool: ...
