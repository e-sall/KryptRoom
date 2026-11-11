"""Real PostgreSQL tests under the restricted PR2 app/operator roles."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from queue import Queue
from threading import Event
from uuid import UUID

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from sqlalchemy.exc import DBAPIError
from test_identity_postgres import (  # reusable real DB provisioning, no mocks
    assert_database_blocker,
)
from test_identity_postgres import (
    cohort as cohort,
)
from test_identity_postgres import (
    stores as stores,
)
from uuid6 import uuid7

from kryptroom_control.modules.authorization import BusinessAction
from kryptroom_control.modules.identity import Principal
from kryptroom_control.operator import Operator
from kryptroom_control.organization_service import AccessError, OrganizationService, active_user
from kryptroom_control.room_schema import rooms
from kryptroom_control.room_service import RoomService

pytestmark = pytest.mark.postgres


def service(s, uid):
    active_user(s, uid)
    return RoomService(OrganizationService(s, Principal(uid)))


def create(app, uid, oid, key="room-key"):
    with app.transaction() as s:
        return service(s, uid).create(oid, "Synthetic Room", "Synthetic metadata", key)


def test_create_retry_read_update_and_isolation(stores, cohort):
    alice, bob, charlie, _, aid, bid, *_ = cohort
    app = stores["app"]
    room = create(app, alice, aid)
    rid = UUID(room["id"])
    assert room["headStateId"] is None and room["status"] == "DRAFT"
    assert create(app, alice, aid) == room
    with app.transaction() as s:
        svc = service(s, alice)
        with pytest.raises(AccessError, match="idempotency_conflict"):
            svc.create(aid, "Changed", "", "room-key")
        assert svc.read(rid) == room
        assert svc.listing(aid, 25, None)["items"] == [room]
        for header, error in ((None, "precondition_required"), ('"9"', "precondition_failed")):
            with pytest.raises(AccessError, match=error):
                svc.update(rid, {"displayName": "No"}, header)
        changed = svc.update(rid, {"displayName": "Updated"}, '"1"')
        assert changed["version"] == 2 and changed["headStateId"] is None
    for uid in (bob, charlie):
        with app.transaction() as s:
            svc = service(s, uid)
            if uid == charlie:
                assert svc.read(rid)["displayName"] == "Updated"
            else:
                assert s.execute(sa.select(rooms).where(rooms.c.id == rid)).first() is None
            for operation in (
                lambda svc=svc: svc.create(aid, "Forbidden", "", "different"),
                lambda svc=svc: svc.update(rid, {"displayName": "Forbidden"}, '"2"'),
            ):
                with pytest.raises(AccessError):
                    operation()
            if uid == bob:
                with pytest.raises(AccessError):
                    svc.read(rid)
                with pytest.raises(AccessError):
                    svc.listing(aid, 25, None)
    assert create(app, bob, bid)["id"] != room["id"]


def test_database_grants_and_no_fake_state(stores, cohort):
    alice, bob, _, _, aid, *_ = cohort
    app = stores["app"]
    rid = UUID(create(app, alice, aid)["id"])
    for statement in (
        "UPDATE control_api.rooms SET head_state_id=gen_random_uuid() WHERE id=:rid",
        "UPDATE control_api.rooms SET organization_id=gen_random_uuid() WHERE id=:rid",
        "DELETE FROM control_api.rooms WHERE id=:rid",
    ):
        with pytest.raises(DBAPIError), app.transaction() as s:
            active_user(s, alice)
            s.execute(sa.text(statement), {"rid": rid})
    with app.transaction() as s:
        active_user(s, bob)
        assert (
            s.execute(
                rooms.update().where(rooms.c.id == rid).values(display_name="Forbidden")
            ).rowcount
            == 0
        )
    with app.transaction() as s:
        assert s.execute(sa.select(rooms)).first() is None  # no actor => deny
    with pytest.raises(DBAPIError), app.transaction() as s:
        active_user(s, bob)
        s.execute(
            rooms.insert().values(
                id=uuid7(), organization_id=aid, created_by_user_id=bob, display_name="Forbidden"
            )
        )
    for role in ("operator", "bff"):
        with pytest.raises(DBAPIError), stores[role].transaction() as s:
            s.execute(sa.select(rooms))


def test_pending_suspended_and_revoked_membership_cannot_create_or_replay(stores, cohort):
    alice, _, charlie, _, aid, _, am, cm, _ = cohort
    app = stores["app"]
    with app.transaction() as s:
        active_user(s, alice)
        pending = OrganizationService(s, Principal(alice)).register(
            "Pending synthetic", str(uuid7())
        )
        with pytest.raises(AccessError):
            RoomService(OrganizationService(s, Principal(alice))).create(
                UUID(pending["id"]), "No", "", "key"
            )
    original = create(app, alice, aid)
    with app.transaction() as s:
        service(s, alice).authority.change_member(aid, cm, "ORG_OWNER", '"1"')
    with app.transaction() as s:
        service(s, charlie).authority.change_member(aid, am, None, '"2"')
    with app.transaction() as s:
        with pytest.raises(AccessError):
            service(s, alice).create(aid, "Synthetic Room", "Synthetic metadata", "room-key")
        with pytest.raises(AccessError):
            service(s, alice).read(UUID(original["id"]))
    with stores["operator"].transaction() as s:
        Operator(s, "synthetic-pr3-controller", "CASE-PR3").set_organization_status(
            aid, "SUSPENDED"
        )
    with app.transaction() as s:
        with pytest.raises(AccessError):
            service(s, charlie).read(UUID(original["id"]))
        with pytest.raises(AccessError):
            service(s, charlie).create(aid, "Synthetic Room", "Synthetic metadata", "room-key")


def test_idempotent_concurrent_creation(stores, cohort):
    alice, _, _, _, aid, *_ = cohort
    app = stores["app"]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: create(app, alice, aid), range(4)))
    assert len({r["id"] for r in results}) == 1
    with app.transaction() as s:
        active_user(s, alice)
        assert (
            s.scalar(
                sa.select(sa.func.count()).select_from(rooms).where(rooms.c.organization_id == aid)
            )
            == 1
        )


def test_admin_create_and_keyset_pagination(stores, cohort):
    alice, _, _, dora, aid, *_ = cohort
    app = stores["app"]
    first = create(app, alice, aid, "owner-key")
    second = create(app, dora, aid, "admin-key")
    assert UUID(first["id"]).version == 7
    with app.transaction() as s:
        svc = service(s, alice)
        page = svc.listing(aid, 1, None)
        assert len(page["items"]) == 1 and page["next_cursor"] is not None
        following = svc.listing(aid, 1, UUID(page["next_cursor"]))
        assert following["next_cursor"] is None
        assert {page["items"][0]["id"], following["items"][0]["id"]} == {first["id"], second["id"]}


def test_controlled_concurrent_if_match(stores, cohort):
    alice, _, _, _, aid, *_ = cohort
    app = stores["app"]
    rid = UUID(create(app, alice, aid)["id"])
    ready, attempting = Queue(), Event()

    def worker():
        with app.transaction() as s:
            svc = service(s, alice)
            svc.authority.authorized(aid, BusinessAction.ORGANIZATION_UPDATE)
            ready.put(s.scalar(sa.text("SELECT pg_backend_pid()")))
            attempting.set()
            try:
                return svc.update(rid, {"displayName": "Second"}, '"1"')
            except AccessError as e:
                return e.code

    with ThreadPoolExecutor(max_workers=1) as pool:
        with app.transaction() as s:
            svc = service(s, alice)
            svc.authority.authorized(aid, BusinessAction.ORGANIZATION_UPDATE, lock=True)
            future = pool.submit(worker)
            assert_database_blocker(s, ready, attempting)
            svc.update(rid, {"displayName": "First"}, '"1"')
        assert future.result(timeout=5) == "precondition_failed"
    with app.transaction() as s:
        assert service(s, alice).read(rid)["displayName"] == "First"


def test_revocation_while_room_mutation_waits(stores, cohort):
    alice, _, _, dora, aid, _, _, _, dm = cohort
    app = stores["app"]
    rid = UUID(create(app, alice, aid)["id"])
    ready, attempting = Queue(), Event()

    def worker():
        with app.transaction() as s:
            svc = service(s, dora)
            svc.authority.authorized(aid, BusinessAction.ORGANIZATION_UPDATE)
            ready.put(s.scalar(sa.text("SELECT pg_backend_pid()")))
            attempting.set()
            try:
                return svc.update(rid, {"displayName": "Forbidden"}, '"1"')
            except AccessError as e:
                return e.code

    with ThreadPoolExecutor(max_workers=1) as pool:
        with app.transaction() as s:
            svc = service(s, alice)
            svc.authority.authorized(aid, BusinessAction.MEMBERS_REVOKE, lock=True)
            future = pool.submit(worker)
            assert_database_blocker(s, ready, attempting)
            svc.authority.change_member(aid, dm, None, '"1"')
        assert future.result(timeout=5) == "resource_not_found"
    with app.transaction() as s:
        assert service(s, alice).read(rid)["version"] == 1


def test_rooms_migration_downgrade_and_reupgrade(postgres_settings):
    # Only the explicitly isolated *_test database selected by conftest.
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    command.downgrade(config, "0002_identity_organizations")
    command.upgrade(config, "head")
    command.upgrade(config, "head")
    command.check(config)
