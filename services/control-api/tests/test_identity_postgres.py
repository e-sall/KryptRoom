"""Real PostgreSQL policy, enrollment, revocation and concurrency acceptance."""

import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import UUID

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from pydantic import SecretStr
from sqlalchemy.exc import DBAPIError
from uuid6 import uuid7

from kryptroom_control.db import Database
from kryptroom_control.identity_schema import memberships, organizations
from kryptroom_control.modules.authorization import BusinessAction
from kryptroom_control.modules.identity import Principal
from kryptroom_control.operator import Operator
from kryptroom_control.organization_service import AccessError, OrganizationService, active_user

pytestmark = pytest.mark.postgres


@pytest.fixture(scope="module")
def stores(postgres_settings, app_password):
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    command.upgrade(config, "head")
    result = {}
    for role in ("app", "operator", "bff"):
        secret = (
            app_password
            if role == "app"
            else SecretStr(
                Path(os.environ[f"CONTROL_TEST_{role.upper()}_PASSWORD_FILE"]).read_text()
            )
        )
        result[role] = Database(
            postgres_settings.model_copy(
                update={
                    "database_user": "kryptroom_" + role,
                    "database_password": secret,
                    "database_password_file": None,
                }
            )
        )
    yield result
    for db in result.values():
        db.close()


def resolve(
    db, subject, *, issuer="https://issuer.example.test/realm", email="shared@example.test"
):
    with db.transaction() as s:
        return s.scalar(
            sa.text("SELECT control_api.resolve_identity(:uid,:lid,:iss,:sub,:label,:email)"),
            {
                "uid": uuid7(),
                "lid": uuid7(),
                "iss": issuer,
                "sub": subject,
                "label": "Synthetic identity",
                "email": email,
            },
        )


def register(db, uid, name="Synthetic Organization", key=None):
    with db.transaction() as s:
        active_user(s, uid)
        return OrganizationService(s, Principal(uid)).register(name, key or str(uuid7()))


def approve(db, oid):
    with db.transaction() as s:
        Operator(s, "synthetic-test-operator", "CASE-PR2").approve(oid)


@pytest.fixture
def cohort(stores):
    app, operator = stores["app"], stores["operator"]
    alice, bob, charlie, dora = [resolve(app, str(uuid7())) for _ in range(4)]
    a, b = register(app, alice), register(app, bob)
    aid, bid = UUID(a["id"]), UUID(b["id"])
    approve(operator, aid)
    approve(operator, bid)
    with operator.transaction() as s:
        op = Operator(s, "synthetic-test-operator", "CASE-PR2")
        cm = op.provision(aid, charlie)
        dm = op.provision(aid, dora, "ORG_ADMIN")
        am = s.scalar(
            sa.select(memberships.c.id).where(
                memberships.c.organization_id == aid, memberships.c.user_id == alice
            )
        )
    return alice, bob, charlie, dora, aid, bid, am, cm, dm


def test_identity_pair_is_only_link_and_concurrent_first_login(stores):
    app = stores["app"]
    subject = str(uuid7())
    with ThreadPoolExecutor(max_workers=4) as pool:
        ids = list(pool.map(lambda _: resolve(app, subject), range(8)))
    assert len(set(ids)) == 1
    uid = ids[0]
    assert uid.version == 7
    assert resolve(app, subject, email="changed@example.test") == uid
    assert resolve(app, str(uuid7())) != uid
    assert resolve(app, subject, issuer="https://other.example.test/realm") != uid
    with app.transaction() as s:
        active_user(s, uid)
        assert OrganizationService(s, Principal(uid)).listing()["items"] == []


def test_controlled_registration_and_retry_safety(stores):
    app, operator = stores["app"], stores["operator"]
    uid = resolve(app, str(uuid7()))
    key = str(uuid7())
    first = register(app, uid, key=key)
    assert first["status"] == "PENDING_REVIEW"
    assert register(app, uid, key=key) == first
    with pytest.raises(AccessError, match="idempotency_conflict"):
        register(app, uid, "Changed request", key)
    oid = UUID(first["id"])
    with app.transaction() as s:
        active_user(s, uid)
        svc = OrganizationService(s, Principal(uid))
        assert svc.listing()["items"] == []
        assert any(o["id"] == str(oid) for o in svc.listing(registrations=True)["items"])
        with pytest.raises(AccessError, match="resource_not_found"):
            svc.authorized(oid, BusinessAction.ORGANIZATION_READ)
        with pytest.raises(AccessError, match="operator_credentials_required"):
            Operator(s, "untrusted", "untrusted").approve(oid)
    approve(operator, oid)
    with pytest.raises(AccessError, match="registration_not_pending"):
        approve(operator, oid)
    with app.transaction() as s:
        active_user(s, uid)
        org, member = OrganizationService(s, Principal(uid)).authorized(
            oid, BusinessAction.ORGANIZATION_READ
        )
        assert org["status"] == member["status"] == "ACTIVE"
        assert member["role"] == "ORG_OWNER"


def test_cross_tenant_read_write_and_missing_context(stores, cohort):
    alice, bob, _, _, aid, bid, *_ = cohort
    app = stores["app"]
    with app.transaction() as s:
        assert s.scalars(sa.select(organizations.c.id)).all() == []
        active_user(s, alice)
        assert bid not in s.scalars(sa.select(organizations.c.id)).all()
        assert (
            s.execute(
                organizations.update()
                .where(organizations.c.id == bid)
                .values(display_name="Unauthorized")
            ).rowcount
            == 0
        )
        with pytest.raises(AccessError, match="resource_not_found"):
            OrganizationService(s, Principal(alice)).authorized(
                bid, BusinessAction.ORGANIZATION_READ
            )
    for sql in (
        "ALTER TABLE control_api.organizations DISABLE ROW LEVEL SECURITY",
        "DELETE FROM control_api.organizations",
        "SET ROLE kryptroom_operator",
        "SET ROLE kryptroom_auth_guard",
        "SELECT * FROM bff_auth.sessions",
        "CREATE TABLE control_api.forbidden(id int)",
    ):
        with pytest.raises(DBAPIError), app.transaction() as s:
            active_user(s, bob)
            s.execute(sa.text(sql))
    with stores["bff"].transaction() as s:
        assert s.scalar(sa.text("SELECT count(*) FROM bff_auth.sessions")) == 0
    with pytest.raises(DBAPIError), stores["bff"].transaction() as s:
        s.execute(sa.select(memberships))
    # Commit, rollback, pool reuse must clear transaction-local principal.
    with pytest.raises(RuntimeError), app.transaction() as s:
        active_user(s, alice)
        raise RuntimeError("synthetic rollback")
    for _ in range(6):
        with app.transaction() as s:
            assert s.scalar(sa.text("SELECT control_api.current_actor()")) is None
            assert s.scalars(sa.select(organizations.c.id)).all() == []


def test_roles_preconditions_and_immediate_revocation(stores, cohort):
    alice, _, charlie, dora, aid, _, am, cm, dm = cohort
    app = stores["app"]
    with app.transaction() as s:
        active_user(s, charlie)
        svc = OrganizationService(s, Principal(charlie))
        with pytest.raises(AccessError, match="permission_denied"):
            svc.member_listing(aid, 25, None)
        with pytest.raises(AccessError, match="permission_denied"):
            svc.change_member(aid, cm, "ORG_OWNER", '"1"')
    with app.transaction() as s:
        active_user(s, dora)
        svc = OrganizationService(s, Principal(dora))
        assert svc.member_listing(aid, 25, None)["items"]
        with pytest.raises(AccessError, match="permission_denied"):
            svc.change_member(aid, dm, "ORG_OWNER", '"1"')
        with pytest.raises(AccessError, match="permission_denied"):
            svc.change_member(aid, am, None, '"2"')
        with pytest.raises(AccessError, match="precondition_required"):
            svc.rename(aid, "New name", None)
        with pytest.raises(AccessError, match="precondition_failed"):
            svc.rename(aid, "New name", '"999"')
        svc.change_member(aid, cm, None, '"1"')
    # A still-valid identity cannot restore the revoked membership.
    with stores["operator"].transaction() as s:
        subject = s.scalar(
            sa.text("SELECT subject FROM control_api.identity_links WHERE user_id=:uid"),
            {"uid": charlie},
        )
    assert resolve(app, subject) == charlie
    with app.transaction() as s:
        active_user(s, charlie)
        with pytest.raises(AccessError, match="resource_not_found"):
            OrganizationService(s, Principal(charlie)).authorized(
                aid, BusinessAction.ORGANIZATION_READ
            )


def test_last_owner_and_concurrent_removals(stores, cohort):
    alice, _, charlie, _, aid, _, am, cm, _ = cohort
    app = stores["app"]
    with app.transaction() as s:
        active_user(s, alice)
        svc = OrganizationService(s, Principal(alice))
        with pytest.raises(AccessError, match="last_owner"):
            svc.change_member(aid, am, None, '"2"')
        svc.change_member(aid, cm, "ORG_OWNER", '"1"')

    def remove(target, version):
        try:
            with app.transaction() as s:
                active_user(s, alice)
                OrganizationService(s, Principal(alice)).change_member(aid, target, None, version)
            return "committed"
        except AccessError:
            return "denied"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda x: remove(*x), [(am, '"2"'), (cm, '"2"')]))
    assert outcomes.count("committed") == 1
    with stores["operator"].transaction() as s:
        assert (
            s.scalar(
                sa.select(sa.func.count())
                .select_from(memberships)
                .where(
                    memberships.c.organization_id == aid,
                    memberships.c.role == "ORG_OWNER",
                    memberships.c.status == "ACTIVE",
                )
            )
            == 1
        )


def test_org_and_user_suspension(stores, cohort):
    alice, _, charlie, _, aid, _, *_ = cohort
    app, operator = stores["app"], stores["operator"]
    with operator.transaction() as s:
        Operator(s, "synthetic-test-operator", "CASE-SUSPEND").set_organization_status(
            aid, "SUSPENDED"
        )
    with app.transaction() as s:
        active_user(s, alice)
        with pytest.raises(AccessError, match="resource_not_found"):
            OrganizationService(s, Principal(alice)).authorized(
                aid, BusinessAction.ORGANIZATION_READ
            )
    with operator.transaction() as s:
        op = Operator(s, "synthetic-test-operator", "CASE-SUSPEND")
        op.set_organization_status(aid, "ACTIVE")
        op.suspend_user(charlie)
    with pytest.raises(AccessError, match="identity_inactive"), app.transaction() as s:
        active_user(s, charlie)
