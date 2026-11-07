"""Transactional business authority. OAuth claims never grant a membership."""

import hashlib
from collections.abc import Mapping
from typing import Any
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session
from uuid6 import uuid7

from kryptroom_control.identity_schema import events, idempotency, memberships, organizations, users
from kryptroom_control.modules.authorization import BusinessAction, ResourceScope
from kryptroom_control.modules.identity import Principal


class AccessError(Exception):
    def __init__(self, status: int, code: str):
        super().__init__(code)
        self.status, self.code = status, code


def require_version(value: str | None, version: int) -> None:
    if value is None:
        raise AccessError(428, "precondition_required")
    if value != f'"{version}"':
        raise AccessError(412, "precondition_failed")


def org_wire(row: Mapping[Any, Any]) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "displayName": row["display_name"],
        "status": row["status"],
        "verificationStatus": row["verification_status"],
        "version": row["version"],
    }


def member_wire(row: Mapping[Any, Any]) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "organizationId": str(row["organization_id"]),
        "userId": str(row["user_id"]),
        "role": row["role"],
        "status": row["status"],
        "version": row["version"],
    }


class OrganizationService:
    def __init__(self, session: Session, principal: Principal):
        self.session, self.principal = session, principal

    def require(self, principal: Principal, action: BusinessAction, scope: ResourceScope) -> None:
        if principal != self.principal:
            raise AccessError(403, "permission_denied")
        self.authorized(scope.organization_id, action)

    def authorized(
        self, organization_id: UUID, action: BusinessAction, *, lock: bool = False
    ) -> tuple[Mapping[Any, Any], Mapping[Any, Any]]:
        if lock:
            # Classify an accessible resource with insufficient role as 403 before
            # UPDATE RLS hides it from a locking SELECT. Re-evaluate after locking.
            self.authorized(organization_id, action)
        # Scope the lookup in SQL through the current principal. A bare ID is not authority.
        query = sa.select(organizations).where(
            organizations.c.id == organization_id,
            organizations.c.status == "ACTIVE",
            sa.exists(
                sa.select(memberships.c.id).where(
                    memberships.c.organization_id == organization_id,
                    memberships.c.user_id == self.principal.user_id,
                    memberships.c.status == "ACTIVE",
                )
            ),
        )
        if lock:
            query = query.with_for_update()
        org = self.session.execute(query).mappings().first()
        if org is None:
            raise AccessError(404, "resource_not_found")
        member_query = sa.select(memberships).where(
            memberships.c.organization_id == organization_id,
            memberships.c.user_id == self.principal.user_id,
            memberships.c.status == "ACTIVE",
        )
        # All membership mutations (including operator provisioning) serialize
        # on the organization row, so the actor stays stable under that lock.
        member = self.session.execute(member_query).mappings().first()
        if member is None:
            raise AccessError(404, "resource_not_found")
        permissions = {
            BusinessAction.ORGANIZATION_READ: {"ORG_OWNER", "ORG_ADMIN", "ORG_MEMBER"},
            BusinessAction.ORGANIZATION_UPDATE: {"ORG_OWNER", "ORG_ADMIN"},
            BusinessAction.MEMBERS_READ: {"ORG_OWNER", "ORG_ADMIN"},
            BusinessAction.MEMBERS_ROLE_CHANGE: {"ORG_OWNER"},
            BusinessAction.MEMBERS_REVOKE: {"ORG_OWNER", "ORG_ADMIN"},
        }
        if member["role"] not in permissions.get(action, set()):
            raise AccessError(403, "permission_denied")
        return org, member

    def event(self, organization_id: UUID, kind: str) -> None:
        self.session.execute(
            events.insert().values(
                id=uuid7(),
                organization_id=organization_id,
                actor_user_id=self.principal.user_id,
                kind=kind,
            )
        )

    def register(self, label: str, key: str) -> dict[str, Any]:
        uid = self.principal.user_id
        digest = hashlib.sha256(label.encode()).hexdigest()
        # Serialize retries before inspecting/creating the idempotency record.
        self.session.execute(
            sa.text("SELECT pg_advisory_xact_lock(hashtextextended(:key,0))"),
            {"key": str(uid) + ":" + key},
        )
        previous = (
            self.session.execute(
                sa.select(idempotency).where(idempotency.c.user_id == uid, idempotency.c.key == key)
            )
            .mappings()
            .first()
        )
        if previous:
            if previous["request_hash"] != digest:
                raise AccessError(409, "idempotency_conflict")
            return dict(previous["response"])
        oid = uuid7()
        row = (
            self.session.execute(
                organizations.insert()
                .values(id=oid, display_name=label, requested_by_user_id=uid)
                .returning(organizations)
            )
            .mappings()
            .one()
        )
        self.session.execute(
            memberships.insert().values(
                id=uuid7(), organization_id=oid, user_id=uid, role="ORG_OWNER", status="PENDING"
            )
        )
        self.event(oid, "registration_requested")
        response = org_wire(row)
        self.session.execute(
            idempotency.insert().values(
                user_id=uid, key=key, request_hash=digest, response=response
            )
        )
        return response

    def listing(
        self, *, registrations: bool = False, limit: int = 25, cursor: UUID | None = None
    ) -> dict[str, Any]:
        query = sa.select(organizations)
        if registrations:
            query = query.where(
                organizations.c.requested_by_user_id == self.principal.user_id,
                organizations.c.status.in_(("PENDING_REVIEW", "REJECTED")),
            )
        else:
            query = query.where(
                organizations.c.status == "ACTIVE",
                sa.exists(
                    sa.select(memberships.c.id).where(
                        memberships.c.organization_id == organizations.c.id,
                        memberships.c.user_id == self.principal.user_id,
                        memberships.c.status == "ACTIVE",
                    )
                ),
            )
        if cursor:
            query = query.where(organizations.c.id > cursor)
        rows = (
            self.session.execute(query.order_by(organizations.c.id).limit(limit + 1))
            .mappings()
            .all()
        )
        return {
            "items": [org_wire(row) for row in rows[:limit]],
            "next_cursor": str(rows[limit - 1]["id"]) if len(rows) > limit else None,
        }

    def rename(self, oid: UUID, label: str, etag: str | None) -> dict[str, Any]:
        org, _ = self.authorized(oid, BusinessAction.ORGANIZATION_UPDATE, lock=True)
        require_version(etag, org["version"])
        row = (
            self.session.execute(
                organizations.update()
                .where(organizations.c.id == oid)
                .values(
                    display_name=label,
                    version=organizations.c.version + 1,
                    updated_at=sa.func.now(),
                )
                .returning(organizations)
            )
            .mappings()
            .one()
        )
        self.event(oid, "metadata_updated")
        return org_wire(row)

    def member_listing(self, oid: UUID, limit: int, cursor: UUID | None) -> dict[str, Any]:
        self.authorized(oid, BusinessAction.MEMBERS_READ)
        query = sa.select(memberships).where(memberships.c.organization_id == oid)
        if cursor:
            query = query.where(memberships.c.id > cursor)
        rows = (
            self.session.execute(query.order_by(memberships.c.id).limit(limit + 1)).mappings().all()
        )
        return {
            "items": [member_wire(row) for row in rows[:limit]],
            "next_cursor": str(rows[limit - 1]["id"]) if len(rows) > limit else None,
        }

    def change_member(
        self, oid: UUID, mid: UUID, role: str | None, etag: str | None
    ) -> dict[str, Any]:
        action = BusinessAction.MEMBERS_ROLE_CHANGE if role else BusinessAction.MEMBERS_REVOKE
        _, actor = self.authorized(oid, action, lock=True)
        target = (
            self.session.execute(
                sa.select(memberships).where(
                    memberships.c.organization_id == oid, memberships.c.id == mid
                )
            )
            .mappings()
            .first()
        )
        if target is None:
            raise AccessError(404, "resource_not_found")
        require_version(etag, target["version"])
        if target["status"] != "ACTIVE":
            raise AccessError(409, "membership_inactive")
        if actor["role"] == "ORG_ADMIN" and target["role"] != "ORG_MEMBER":
            raise AccessError(403, "permission_denied")
        self.session.execute(
            sa.select(memberships.c.id)
            .where(memberships.c.id == mid, memberships.c.organization_id == oid)
            .with_for_update()
        ).one()
        if target["role"] == "ORG_OWNER" and role != "ORG_OWNER":
            owners = self.session.scalar(
                sa.text("SELECT control_api.active_owner_count(:oid,:excluded)"),
                {"oid": oid, "excluded": target["user_id"]},
            )
            if owners is None or owners < 1:
                raise AccessError(409, "last_owner")
        values: dict[str, Any] = {"version": memberships.c.version + 1, "updated_at": sa.func.now()}
        if role:
            values["role"] = role
        else:
            values.update(status="REVOKED", revoked_at=sa.func.now())
        self.session.execute(memberships.update().where(memberships.c.id == mid).values(**values))
        self.event(oid, "member_role_changed" if role else "membership_revoked")
        return member_wire(
            {
                **dict(target),
                **({"role": role} if role else {"status": "REVOKED"}),
                "version": target["version"] + 1,
            }
        )


def active_user(session: Session, uid: UUID) -> Mapping[Any, Any]:
    session.execute(sa.text("SELECT set_config('kryptroom.user_id',:uid,true)"), {"uid": str(uid)})
    if not session.scalar(sa.text("SELECT control_api.lock_current_user()")):
        raise AccessError(403, "identity_inactive")
    user = session.execute(sa.select(users).where(users.c.id == uid)).mappings().first()
    if user is None or user["status"] != "ACTIVE":
        raise AccessError(403, "identity_inactive")
    return user
