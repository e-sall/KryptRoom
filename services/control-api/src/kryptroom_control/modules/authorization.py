from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol
from uuid import UUID

from kryptroom_control.contracts import BusinessError
from kryptroom_control.modules.identity import Principal


class BusinessAction(StrEnum):
    ORGANIZATION_REGISTER = "organization.register"
    ORGANIZATION_READ = "organization.read"
    ORGANIZATION_UPDATE = "organization.update"
    MEMBERS_READ = "organization.members.read"
    MEMBERS_ROLE_CHANGE = "organization.members.role.change"
    MEMBERS_REVOKE = "organization.members.revoke"
    ROOM_READ = "room.read"


@dataclass(frozen=True)
class ResourceScope:
    organization_id: UUID
    room_id: UUID | None = None


class BusinessAuthorizer(Protocol):
    def require(
        self, principal: Principal, action: BusinessAction, scope: ResourceScope
    ) -> None: ...


class DenyAllAuthorizer:
    """Safe default. Never translates business access into cryptographic authorization."""

    def require(self, principal: Principal, action: BusinessAction, scope: ResourceScope) -> None:
        raise BusinessError("permission_denied")
