"""Isolated pilot operations; never mounted as an HTTP approval endpoint."""

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session
from uuid6 import uuid7

from kryptroom_control.identity_schema import events, memberships, organizations, users
from kryptroom_control.organization_service import AccessError


class Operator:
    def __init__(self, session: Session, attribution: str, case: str):
        if session.scalar(sa.text("SELECT current_user")) != "kryptroom_operator":
            raise AccessError(403, "operator_credentials_required")
        if not all(1 <= len(value.strip()) <= 120 for value in (attribution, case)):
            raise ValueError("Operator attribution and case are required")
        self.session, self.attribution, self.case = session, attribution, case

    def event(self, oid: UUID | None, kind: str) -> None:
        self.session.execute(
            events.insert().values(
                id=uuid7(),
                organization_id=oid,
                operator_reference=self.attribution,
                case_reference=self.case,
                kind=kind,
            )
        )

    def approve(self, oid: UUID) -> None:
        applicant_id = self.session.scalar(
            sa.select(organizations.c.requested_by_user_id).where(organizations.c.id == oid)
        )
        if applicant_id is None:
            raise AccessError(409, "registration_not_pending")
        applicant = (
            self.session.execute(
                sa.select(users).where(users.c.id == applicant_id).with_for_update(read=True)
            )
            .mappings()
            .one()
        )
        if applicant["status"] != "ACTIVE":
            raise AccessError(409, "applicant_inactive")
        org = (
            self.session.execute(
                sa.select(organizations).where(organizations.c.id == oid).with_for_update()
            )
            .mappings()
            .one_or_none()
        )
        if org is None or org["status"] != "PENDING_REVIEW":
            raise AccessError(409, "registration_not_pending")
        owner = (
            self.session.execute(
                sa.select(memberships)
                .where(
                    memberships.c.organization_id == oid,
                    memberships.c.user_id == org["requested_by_user_id"],
                    memberships.c.role == "ORG_OWNER",
                    memberships.c.status == "PENDING",
                )
                .with_for_update()
            )
            .mappings()
            .one_or_none()
        )
        if owner is None:
            raise AccessError(409, "registration_inconsistent")
        self.session.execute(
            organizations.update()
            .where(organizations.c.id == oid)
            .values(
                status="ACTIVE",
                verification_status="REVIEWED",
                review_reference=self.case,
                reviewed_at=sa.func.now(),
                updated_at=sa.func.now(),
                version=organizations.c.version + 1,
            )
        )
        self.session.execute(
            memberships.update()
            .where(memberships.c.id == owner["id"])
            .values(
                status="ACTIVE",
                activated_at=sa.func.now(),
                updated_at=sa.func.now(),
                version=memberships.c.version + 1,
            )
        )
        self.event(oid, "registration_approved")

    def provision(self, oid: UUID, uid: UUID, role: str = "ORG_MEMBER") -> UUID:
        if role not in {"ORG_OWNER", "ORG_ADMIN", "ORG_MEMBER"}:
            raise ValueError("Invalid membership role")
        user = (
            self.session.execute(
                sa.select(users).where(users.c.id == uid).with_for_update(read=True)
            )
            .mappings()
            .one_or_none()
        )
        org = (
            self.session.execute(
                sa.select(organizations).where(organizations.c.id == oid).with_for_update()
            )
            .mappings()
            .one_or_none()
        )
        if org is None or org["status"] != "ACTIVE" or user is None or user["status"] != "ACTIVE":
            raise AccessError(409, "enrollment_unavailable")
        if self.session.scalar(
            sa.select(memberships.c.id).where(
                memberships.c.organization_id == oid, memberships.c.user_id == uid
            )
        ):
            raise AccessError(409, "enrollment_exists")
        mid = uuid7()
        self.session.execute(
            memberships.insert().values(
                id=mid,
                organization_id=oid,
                user_id=uid,
                role=role,
                status="ACTIVE",
                activated_at=sa.func.now(),
            )
        )
        self.event(oid, "member_provisioned")
        return mid

    def set_organization_status(self, oid: UUID, status: str) -> None:
        if status not in {"SUSPENDED", "ACTIVE", "REJECTED"}:
            raise ValueError("Invalid operator status")
        org = (
            self.session.execute(
                sa.select(organizations).where(organizations.c.id == oid).with_for_update()
            )
            .mappings()
            .one_or_none()
        )
        allowed = {("ACTIVE", "SUSPENDED"), ("SUSPENDED", "ACTIVE"), ("PENDING_REVIEW", "REJECTED")}
        if org is None or (org["status"], status) not in allowed:
            raise AccessError(409, "invalid_status_transition")
        if status == "ACTIVE" and not self.active_owners(oid):
            raise AccessError(409, "active_owner_required")
        self.session.execute(
            organizations.update()
            .where(organizations.c.id == oid)
            .values(status=status, updated_at=sa.func.now(), version=organizations.c.version + 1)
        )
        self.event(oid, "organization_" + status.lower())

    def suspend_user(self, uid: UUID) -> None:
        row = (
            self.session.execute(sa.select(users).where(users.c.id == uid).with_for_update())
            .mappings()
            .one_or_none()
        )
        if row is None:
            raise AccessError(404, "resource_not_found")
        owned = self.session.scalars(
            sa.select(organizations.c.id)
            .where(
                organizations.c.status == "ACTIVE",
                sa.exists(
                    sa.select(memberships.c.id).where(
                        memberships.c.organization_id == organizations.c.id,
                        memberships.c.user_id == uid,
                        memberships.c.role == "ORG_OWNER",
                        memberships.c.status == "ACTIVE",
                    )
                ),
            )
            .order_by(organizations.c.id)
            .with_for_update()
        ).all()
        self.session.execute(
            users.update()
            .where(users.c.id == uid)
            .values(status="SUSPENDED", version=users.c.version + 1, updated_at=sa.func.now())
        )
        for oid in owned:
            if not self.active_owners(oid):
                self.session.execute(
                    organizations.update()
                    .where(organizations.c.id == oid)
                    .values(
                        status="SUSPENDED",
                        updated_at=sa.func.now(),
                        version=organizations.c.version + 1,
                    )
                )
                self.event(oid, "organization_suspended_last_owner")
        self.event(None, "user_suspended")

    def active_owners(self, oid: UUID) -> int:
        return int(
            self.session.scalar(
                sa.select(sa.func.count())
                .select_from(memberships.join(users, users.c.id == memberships.c.user_id))
                .where(
                    memberships.c.organization_id == oid,
                    memberships.c.role == "ORG_OWNER",
                    memberships.c.status == "ACTIVE",
                    users.c.status == "ACTIVE",
                )
            )
            or 0
        )
