"""Bounded metadata collaboration; no cryptographic authority."""

import re
from typing import Any
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.exc import DBAPIError

from kryptroom_control.modules.authorization import BusinessAction
from kryptroom_control.organization_service import AccessError, OrganizationService


def wire(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "roomId": str(row["room_id"]),
        "ownerOrganizationId": str(row["owner_id"]),
        "targetOrganizationId": str(row["target_id"]),
        "status": row["status"],
        "version": row["version"],
    }


class Collaboration:
    def __init__(self, authority: OrganizationService):
        self.authority = authority
        self.session = authority.session

    def history(self, rid: UUID, limit: int, cursor: UUID | None) -> dict[str, Any]:
        try:
            with self.session.begin_nested():
                rows = (
                    self.session.execute(
                        sa.text("SELECT * FROM control_api.room_history(:rid,:cursor,:limit)"),
                        {"rid": rid, "cursor": cursor, "limit": limit + 1},
                    )
                    .mappings()
                    .all()
                )
        except DBAPIError as error:
            code = str(getattr(error.orig, "sqlstate", ""))
            status, reason = {
                "42501": (403, "permission_denied"),
                "22023": (422, "invalid_page"),
            }.get(code, (503, "history_unavailable"))
            raise AccessError(status, reason) from None
        return {
            "items": [
                {
                    "id": str(r["id"]),
                    "kind": r["kind"],
                    "actorOrganizationId": str(r["actor_organization_id"]),
                    "createdAt": r["created_at"].isoformat(),
                }
                for r in rows[:limit]
            ],
            "next_cursor": str(rows[limit - 1]["id"]) if len(rows) > limit else None,
        }

    def listing(self, oid: UUID, limit: int, cursor: UUID | None) -> dict[str, Any]:
        self.authority.authorized(oid, BusinessAction.ORGANIZATION_UPDATE)
        rows = (
            self.session.execute(
                sa.text("""SELECT * FROM control_api.room_invitations
          WHERE (owner_id=:oid OR target_id=:oid) AND (CAST(:cursor AS uuid) IS NULL OR id>:cursor)
          ORDER BY id LIMIT :limit"""),
                {"oid": oid, "cursor": cursor, "limit": limit + 1},
            )
            .mappings()
            .all()
        )
        return {
            "items": [wire(dict(r)) for r in rows[:limit]],
            "next_cursor": str(rows[limit - 1]["id"]) if len(rows) > limit else None,
        }

    def mutate(
        self,
        oid: UUID,
        rid: UUID,
        action: str,
        iid: UUID | None = None,
        target: UUID | None = None,
        key: str | None = None,
        etag: str | None = None,
    ) -> dict[str, Any]:
        self.authority.authorized(oid, BusinessAction.ORGANIZATION_UPDATE, lock=True)
        expected = None
        if action != "invite":
            if etag is None:
                raise AccessError(428, "precondition_required")
            if not re.fullmatch(r'"[1-9][0-9]{0,9}"', etag):
                raise AccessError(412, "precondition_failed")
            expected = int(etag[1:-1])
            if expected < 1 or expected > 2147483647:
                raise AccessError(412, "precondition_failed")
        try:
            with self.session.begin_nested():
                row = self.session.scalar(
                    sa.text(
                        "SELECT control_api.room_collaboration("
                        ":rid,:oid,:iid,:action,:expected,:target,:key)"
                    ),
                    {
                        "rid": rid,
                        "oid": oid,
                        "iid": iid or uuid4(),
                        "action": action,
                        "expected": expected,
                        "target": target,
                        "key": key,
                    },
                )
        except DBAPIError as error:
            state = str(getattr(error.orig, "sqlstate", ""))
            status, code = {
                "P0002": (404, "resource_not_found"),
                "42501": (403, "permission_denied"),
                "23505": (409, "collaboration_conflict"),
                "40001": (412, "precondition_failed"),
                "22023": (422, "invalid_collaboration"),
            }.get(state, (503, "collaboration_unavailable"))
            raise AccessError(status, code) from None
        return wire(row)
