"""Real PostgreSQL policy, enrollment, revocation and concurrency acceptance."""

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from queue import Queue
from threading import Event
from uuid import UUID

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from pydantic import SecretStr
from sqlalchemy.exc import DBAPIError, IntegrityError
from uuid6 import uuid7

from kryptroom_control.db import Database
from kryptroom_control.identity_schema import logout_replays, memberships, organizations, sessions
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


def test_revoked_requester_cannot_read_active_org_but_can_read_own_requests(stores, cohort):
    alice, bob, charlie, _, aid, _, am, cm, _ = cohort
    app, operator = stores["app"], stores["operator"]
    pending = register(app, alice, "Own pending request")
    rejected = register(app, alice, "Own rejected request")
    foreign = register(app, bob, "Foreign pending request")
    with operator.transaction() as s:
        Operator(s, "synthetic-test-operator", "CASE-REQUESTER").set_organization_status(
            UUID(rejected["id"]), "REJECTED"
        )
    with app.transaction() as s:
        active_user(s, alice)
        OrganizationService(s, Principal(alice)).change_member(aid, cm, "ORG_OWNER", '"1"')
    with app.transaction() as s:
        active_user(s, charlie)
        OrganizationService(s, Principal(charlie)).change_member(aid, am, None, '"2"')
    with app.transaction() as s:
        active_user(s, alice)
        # Direct SQL under kryptroom_app: no service membership predicate can hide an RLS bug.
        visible = set(s.scalars(sa.select(organizations.c.id)).all())
        assert aid not in visible
        assert {UUID(pending["id"]), UUID(rejected["id"])} <= visible
        assert UUID(foreign["id"]) not in visible
        service = OrganizationService(s, Principal(alice))
        assert all(row["id"] != str(aid) for row in service.listing()["items"])
        requests = {row["id"] for row in service.listing(registrations=True)["items"]}
        assert {pending["id"], rejected["id"]} <= requests
        with pytest.raises(AccessError, match="resource_not_found"):
            service.authorized(aid, BusinessAction.ORGANIZATION_READ)


def blocked_worker(app, uid, oid, action, mutate, ready, attempting):
    """A real second connection signals only after its initial authorization succeeds."""
    try:
        with app.transaction() as s:
            s.execute(sa.text("SET LOCAL statement_timeout='8s'"))
            active_user(s, uid)
            service = OrganizationService(s, Principal(uid))
            service.authorized(oid, action)
            connection = s.connection()
            ready.put(s.scalar(sa.text("SELECT pg_backend_pid()")))

            def before_execute(conn, cursor, statement, parameters, context, many):
                if "control_api.organizations" in statement and "FOR UPDATE" in statement:
                    attempting.set()

            sa.event.listen(connection, "before_cursor_execute", before_execute)
            try:
                mutate(service)
            finally:
                sa.event.remove(connection, "before_cursor_execute", before_execute)
        return {"outcome": "committed"}
    except AccessError as error:
        return {"outcome": "denied", "status": error.status, "code": error.code}


def assert_database_blocker(session, ready, attempting):
    worker_pid = ready.get(timeout=3)
    blocker_pid = session.scalar(sa.text("SELECT pg_backend_pid()"))
    assert worker_pid != blocker_pid
    assert attempting.wait(timeout=3), "Worker never attempted the authorized locking statement"
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        blockers = session.scalar(sa.text("SELECT pg_blocking_pids(:pid)"), {"pid": worker_pid})
        if blocker_pid in blockers:
            print(
                json.dumps(
                    {
                        "initial_authorization": "passed",
                        "distinct_connections": True,
                        "worker_pid": worker_pid,
                        "blocker_pid": blocker_pid,
                        "postgres_lock_wait_observed": True,
                    }
                )
            )
            return
        # Bounded polling observes an actual PostgreSQL wait; time alone never passes the test.
        time.sleep(0.01)
    pytest.fail("The expected real PostgreSQL lock overlap was not observed")


def test_mutation_rechecks_authorization_after_blocked_revocation(stores, cohort):
    alice, _, _, dora, aid, _, _, _, dm = cohort
    app = stores["app"]
    ready, attempting = Queue(), Event()
    with ThreadPoolExecutor(max_workers=1) as pool:
        with app.transaction() as s:
            active_user(s, alice)
            service = OrganizationService(s, Principal(alice))
            original, _ = service.authorized(aid, BusinessAction.MEMBERS_REVOKE, lock=True)
            name, version = original["display_name"], original["version"]
            future = pool.submit(
                blocked_worker,
                app,
                dora,
                aid,
                BusinessAction.ORGANIZATION_UPDATE,
                lambda worker: worker.rename(
                    aid, "Forbidden after committed revocation", f'"{version}"'
                ),
                ready,
                attempting,
            )
            assert_database_blocker(s, ready, attempting)
            service.change_member(aid, dm, None, '"1"')
        # Commit and release the controlled lock before joining the second connection.
        print(json.dumps({"revocation": "committed_before_worker_resume"}))
        result = future.result(timeout=5)
    assert result == {"outcome": "denied", "status": 404, "code": "resource_not_found"}
    with stores["operator"].transaction() as s:
        row = s.execute(sa.select(organizations).where(organizations.c.id == aid)).mappings().one()
        assert row["display_name"] == name and row["version"] == version
    print(json.dumps({"resumed_mutation": result, "forbidden_change_persisted": False}))


def test_last_owner_and_concurrent_removals(stores, cohort):
    alice, _, charlie, _, aid, _, am, cm, _ = cohort
    app = stores["app"]
    with app.transaction() as s:
        active_user(s, alice)
        svc = OrganizationService(s, Principal(alice))
        with pytest.raises(AccessError, match="last_owner"):
            svc.change_member(aid, am, None, '"2"')
        svc.change_member(aid, cm, "ORG_OWNER", '"1"')

    ready, attempting = Queue(), Event()
    with ThreadPoolExecutor(max_workers=1) as pool:
        with app.transaction() as s:
            active_user(s, alice)
            service = OrganizationService(s, Principal(alice))
            service.authorized(aid, BusinessAction.MEMBERS_REVOKE, lock=True)
            future = pool.submit(
                blocked_worker,
                app,
                alice,
                aid,
                BusinessAction.MEMBERS_REVOKE,
                lambda worker: worker.change_member(aid, am, None, '"2"'),
                ready,
                attempting,
            )
            assert_database_blocker(s, ready, attempting)
            service.change_member(aid, cm, None, '"2"')
        result = future.result(timeout=5)
    assert result == {"outcome": "denied", "status": 409, "code": "last_owner"}
    print(json.dumps({"first_owner_removal": "committed", "overlapping_second_removal": result}))
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


def test_suspending_last_effective_owner_suspends_org_fail_closed(stores, cohort):
    alice, _, charlie, _, aid, _, *_ = cohort
    with stores["operator"].transaction() as s:
        op = Operator(s, "synthetic-test-operator", "CASE-LAST-OWNER")
        op.suspend_user(alice)
        assert (
            s.scalar(sa.select(organizations.c.status).where(organizations.c.id == aid))
            == "SUSPENDED"
        )
        with pytest.raises(AccessError, match="active_owner_required"):
            op.set_organization_status(aid, "ACTIVE")
    with stores["app"].transaction() as s:
        active_user(s, charlie)
        with pytest.raises(AccessError, match="resource_not_found"):
            OrganizationService(s, Principal(charlie)).authorized(
                aid, BusinessAction.ORGANIZATION_READ
            )


def test_suspended_owner_cannot_count_as_a_remaining_owner(stores, cohort):
    alice, _, charlie, _, aid, _, am, cm, _ = cohort
    with stores["app"].transaction() as s:
        active_user(s, alice)
        OrganizationService(s, Principal(alice)).change_member(aid, cm, "ORG_OWNER", '"1"')
    with stores["operator"].transaction() as s:
        Operator(s, "synthetic-test-operator", "CASE-OWNER").suspend_user(charlie)
    with stores["app"].transaction() as s:
        active_user(s, alice)
        service = OrganizationService(s, Principal(alice))
        with pytest.raises(AccessError, match="last_owner"):
            service.change_member(aid, am, None, '"2"')
        # Removing an already ineffective owner does not remove the effective owner.
        service.change_member(aid, cm, None, '"2"')


def test_rls_helpers_are_nonlogin_scoped_and_runtime_cannot_disable_filtering(stores, cohort):
    alice, _, _, _, aid, bid, *_ = cohort
    with stores["app"].transaction() as s:
        active_user(s, alice)
        assert (
            s.scalar(
                sa.text("SELECT control_api.active_owner_count(:oid,:excluded)"),
                {"oid": bid, "excluded": alice},
            )
            == 0
        )
        assert (
            s.scalar(
                sa.text("SELECT rolcanlogin FROM pg_roles WHERE rolname='kryptroom_auth_guard'")
            )
            is False
        )
        assert (
            s.scalar(
                sa.text(
                    "SELECT has_schema_privilege('kryptroom_auth_guard','control_api','CREATE')"
                )
            )
            is False
        )
        assert (
            s.scalar(
                sa.text(
                    "SELECT has_table_privilege('kryptroom_auth_guard', "
                    "(SELECT c.oid FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
                    "WHERE n.nspname='bff_auth' AND c.relname='sessions'),'SELECT')"
                )
            )
            is False
        )
        assert (
            s.scalar(
                sa.text(
                    "SELECT count(*) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace "
                    "WHERE n.nspname='control_api' AND p.prosecdef "
                    "AND NOT coalesce('search_path=pg_catalog'=ANY(p.proconfig),false)"
                )
            )
            == 0
        )
    with pytest.raises(DBAPIError), stores["app"].transaction() as s:
        active_user(s, alice)
        s.execute(sa.text("SET LOCAL row_security=off"))
        s.execute(sa.select(organizations).where(organizations.c.id == aid))


def test_bff_user_reference_and_logout_replay_constraints(stores):
    with pytest.raises(IntegrityError), stores["bff"].transaction() as s:
        s.execute(
            sessions.insert().values(
                id_hash=uuid7().hex + uuid7().hex,
                user_id=uuid7(),
                issuer="https://synthetic.example.test/realm",
                subject="missing-user",
                encrypted_access_token=uuid7().hex,
                encryption_key_id="test",
            )
        )
    jti = str(uuid7())
    with stores["bff"].transaction() as s:
        s.execute(logout_replays.insert().values(issuer="https://synthetic.example.test", jti=jti))
    with pytest.raises(IntegrityError), stores["bff"].transaction() as s:
        s.execute(logout_replays.insert().values(issuer="https://synthetic.example.test", jti=jti))
