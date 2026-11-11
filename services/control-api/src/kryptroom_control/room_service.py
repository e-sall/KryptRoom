"""Business metadata only, using current PR2 identity/membership authority."""

import hashlib
import json
from collections.abc import Mapping
from typing import Any
from uuid import UUID

import sqlalchemy as sa
from uuid6 import uuid7

from kryptroom_control.modules.authorization import BusinessAction
from kryptroom_control.organization_service import AccessError, OrganizationService, require_version
from kryptroom_control.room_schema import room_requests, rooms


def room_wire(row: Mapping[Any, Any]) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "organizationId": str(row["organization_id"]),
        "displayName": row["display_name"],
        "description": row["description"],
        "status": row["status"],
        "headStateId": None,
        "version": row["version"],
    }


class RoomService:
    def __init__(self, authority: OrganizationService):
        self.authority = authority
        self.session = authority.session

    def create(self, oid: UUID, label: str, description: str, key: str) -> dict[str, Any]:
        # Same lock as PR2 membership mutations; recheck authority after waiting.
        self.authority.authorized(oid, BusinessAction.ORGANIZATION_UPDATE, lock=True)
        digest = hashlib.sha256(
            json.dumps([label, description], ensure_ascii=False).encode()
        ).hexdigest()
        uid = self.authority.principal.user_id
        self.session.execute(
            sa.text("SELECT pg_advisory_xact_lock(hashtextextended(:key,0))"),
            {"key": json.dumps([str(uid), str(oid), key])},
        )
        previous = (
            self.session.execute(
                sa.select(room_requests).where(
                    room_requests.c.user_id == uid,
                    room_requests.c.organization_id == oid,
                    room_requests.c.key == key,
                )
            )
            .mappings()
            .first()
        )
        if previous:
            if previous["request_hash"] != digest:
                raise AccessError(409, "idempotency_conflict")
            return dict(previous["response"])
        row = (
            self.session.execute(
                rooms.insert()
                .values(
                    id=uuid7(),
                    organization_id=oid,
                    created_by_user_id=uid,
                    display_name=label,
                    description=description,
                )
                .returning(rooms)
            )
            .mappings()
            .one()
        )
        response = room_wire(row)
        self.session.execute(
            room_requests.insert().values(
                user_id=uid, organization_id=oid, key=key, request_hash=digest, response=response
            )
        )
        self.authority.event(oid, "room_created")
        return response

    def listing(self, oid: UUID, limit: int, cursor: UUID | None) -> dict[str, Any]:
        self.authority.authorized(oid, BusinessAction.ORGANIZATION_READ)
        query = sa.select(rooms).where(
            sa.or_(
                rooms.c.organization_id == oid,
                rooms.c.id.in_(sa.select(sa.func.control_api.shared_room_ids(oid))),
            )
        )
        if cursor:
            query = query.where(rooms.c.id > cursor)
        rows = self.session.execute(query.order_by(rooms.c.id).limit(limit + 1)).mappings().all()
        return {
            "items": [room_wire(row) for row in rows[:limit]],
            "next_cursor": str(rows[limit - 1]["id"]) if len(rows) > limit else None,
        }

    def _room(self, rid: UUID, *, lock: bool = False) -> Mapping[Any, Any]:
        query = sa.select(rooms).where(rooms.c.id == rid)
        if lock:
            query = query.with_for_update()
        row = self.session.execute(query).mappings().first()
        if row is None:
            raise AccessError(404, "resource_not_found")
        return row

    def read(self, rid: UUID) -> dict[str, Any]:
        row = self._room(rid)
        return room_wire(row)

    def update(self, rid: UUID, changes: dict[str, str], etag: str | None) -> dict[str, Any]:
        row = self._room(rid)
        self.authority.authorized(
            row["organization_id"], BusinessAction.ORGANIZATION_UPDATE, lock=True
        )
        row = self._room(rid, lock=True)
        require_version(etag, row["version"])
        values: dict[str, Any] = {"version": rooms.c.version + 1, "updated_at": sa.func.now()}
        if "displayName" in changes:
            values["display_name"] = changes["displayName"]
        if "description" in changes:
            values["description"] = changes["description"]
        result = (
            self.session.execute(
                rooms.update().where(rooms.c.id == rid).values(**values).returning(rooms)
            )
            .mappings()
            .one()
        )
        self.authority.event(row["organization_id"], "room_metadata_updated")
        return room_wire(result)
