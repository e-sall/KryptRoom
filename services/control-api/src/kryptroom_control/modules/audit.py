from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from sqlalchemy.orm import Session


@dataclass(frozen=True)
class AuditReference:
    """References only; no arbitrary payload, tokens, dataset or cryptographic material."""

    event_id: UUID
    actor_user_id: UUID
    resource_id: UUID
    correlation_id: UUID


class TransactionalAuditWriter(Protocol):
    """Future PR6 audit + outbox must use the caller's transaction. No proof claim."""

    def append(self, session: Session, event: AuditReference) -> None: ...
