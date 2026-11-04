from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from pydantic import SecretStr


@dataclass(frozen=True)
class Principal:
    user_id: UUID


class IdentityVerifier(Protocol):
    """PR2 must validate OIDC issuer/audience/signature before resolving an internal user."""

    def verify(self, access_token: SecretStr) -> Principal: ...
