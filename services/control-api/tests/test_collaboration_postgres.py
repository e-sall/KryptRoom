from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Event
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import DBAPIError
from test_identity_postgres import approve, assert_database_blocker, register, resolve
from test_identity_postgres import cohort as cohort
from test_identity_postgres import stores as stores

from kryptroom_control.collaboration import Collaboration
from kryptroom_control.db import Database
from kryptroom_control.modules.authorization import BusinessAction
from kryptroom_control.modules.identity import Principal
from kryptroom_control.operator import Operator
from kryptroom_control.organization_service import AccessError, OrganizationService, active_user
from kryptroom_control.room_service import RoomService

pytestmark = pytest.mark.postgres


def svc(s, uid):
    active_user(s, uid)
    return OrganizationService(s, Principal(uid))


@pytest.fixture
def invitation(stores, cohort):
    a, b, _, _, aid, bid, *_ = cohort
    with stores["app"].transaction() as s:
        authority = svc(s, a)
        room = RoomService(authority).create(aid, "Shared synthetic", "", str(uuid4()))
        invite = Collaboration(authority).mutate(
            aid, UUID(room["id"]), "invite", target=bid, key="test-key"
        )
        assert (
            Collaboration(authority).mutate(
                aid, UUID(room["id"]), "invite", target=bid, key="test-key"
            )
            == invite
        )
    return a, b, aid, bid, UUID(room["id"]), UUID(invite["id"])


def test_accept_isolation_and_direct_sql(stores, invitation):
    a, b, aid, bid, rid, iid = invitation
    app = stores["app"]
    with app.transaction() as s:
        auth = svc(s, b)
        with pytest.raises(AccessError):
            RoomService(auth).read(rid)
        assert Collaboration(auth).listing(bid, 25, None)["items"][0]["status"] == "PENDING"
        accepted = Collaboration(auth).mutate(bid, rid, "accept", iid=iid, etag='"1"')
        assert accepted["status"] == "ACCEPTED"
        assert RoomService(auth).read(rid)["headStateId"] is None
        assert RoomService(auth).listing(bid, 25, None)["items"][0]["id"] == str(rid)
        with pytest.raises(AccessError):
            RoomService(auth).update(rid, {"displayName": "Forbidden"}, '"1"')
    c = resolve(app, str(uuid4()))
    co = UUID(register(app, c)["id"])
    approve(stores["operator"], co)
    with app.transaction() as s:
        auth = svc(s, c)
        with pytest.raises(AccessError):
            RoomService(auth).read(rid)
        assert Collaboration(auth).listing(co, 25, None)["items"] == []
        with pytest.raises(AccessError):
            Collaboration(auth).mutate(co, rid, "accept", iid=iid, etag='"1"')
        with pytest.raises(AccessError):
            Collaboration(auth).mutate(co, rid, "invite", target=bid, key="forged")
    with pytest.raises(DBAPIError), app.transaction() as s:
        svc(s, b)
        s.execute(
            sa.text("UPDATE control_api.room_invitations SET status='ACCEPTED' WHERE id=:iid"),
            {"iid": iid},
        )
    with app.transaction() as s:
        auth = svc(s, a)
        assert (
            s.scalar(
                sa.text("SELECT count(*) FROM control_api.room_participants(:rid)"), {"rid": rid}
            )
            == 1
        )
        Collaboration(auth).mutate(aid, rid, "revoke", iid=iid, etag='"2"')
    with app.transaction() as s:
        with pytest.raises(AccessError):
            RoomService(svc(s, b)).read(rid)


@pytest.mark.parametrize("action", ["reject", "leave"])
def test_target_terminal_states(stores, invitation, action):
    _, b, _, bid, rid, iid = invitation
    with stores["app"].transaction() as s:
        c = Collaboration(svc(s, b))
        if action == "leave":
            c.mutate(bid, rid, "accept", iid=iid, etag='"1"')
        row = c.mutate(bid, rid, action, iid=iid, etag='"1"' if action == "reject" else '"2"')
        assert row["status"] == ("REJECTED" if action == "reject" else "LEFT")
        assert c.mutate(bid, rid, action, iid=iid, etag='"1"') == row
        with pytest.raises(AccessError):
            RoomService(c.authority).read(rid)


def test_revocation_wins_over_blocked_accept(stores, invitation):
    a, b, aid, bid, rid, iid = invitation
    app = stores["app"]
    ready, attempt = Queue(), Event()

    def worker():
        with app.transaction() as s:
            auth = svc(s, b)
            auth.authorized(
                bid,
                BusinessAction.ORGANIZATION_UPDATE,
            )
            ready.put(s.scalar(sa.text("SELECT pg_backend_pid()")))
            attempt.set()
            try:
                return Collaboration(auth).mutate(bid, rid, "accept", iid=iid, etag='"1"')
            except AccessError as e:
                return e.status

    with ThreadPoolExecutor(max_workers=1) as pool:
        with app.transaction() as s:
            auth = svc(s, a)
            s.execute(
                sa.text("SELECT id FROM control_api.rooms WHERE id=:rid FOR UPDATE"), {"rid": rid}
            )
            f = pool.submit(worker)
            assert_database_blocker(s, ready, attempt)
            Collaboration(auth).mutate(aid, rid, "revoke", iid=iid, etag='"1"')
        assert f.result(timeout=5) == 412
    with app.transaction() as s:
        with pytest.raises(AccessError):
            RoomService(svc(s, b)).read(rid)


def test_member_denied_admin_allowed_and_one_partner(stores, cohort):
    a, b, member, admin, aid, bid, *_ = cohort
    app = stores["app"]
    with app.transaction() as s:
        rid = UUID(RoomService(svc(s, a)).create(aid, "Roles", "", str(uuid4()))["id"])
    with app.transaction() as s:
        with pytest.raises(AccessError):
            Collaboration(svc(s, member)).mutate(aid, rid, "invite", target=bid, key="no")
    with app.transaction() as s:
        c = Collaboration(svc(s, admin))
        item = c.mutate(aid, rid, "invite", target=bid, key="one")
        assert UUID(item["id"]).version == 4
        for key, target in (("two", bid), ("one", aid)):
            with pytest.raises(AccessError) as error:
                c.mutate(aid, rid, "invite", target=target, key=key)
            assert error.value.status == 409
    with app.transaction() as s:
        c = Collaboration(svc(s, b))
        for etag, status in (
            (None, 428),
            ('"9"', 412),
            ('W/"1"', 412),
            ('"²"', 412),
            ('"' + "9" * 5000 + '"', 412),
        ):
            with pytest.raises(AccessError) as error:
                c.mutate(bid, rid, "accept", iid=UUID(item["id"]), etag=etag)
            assert error.value.status == status
        c.mutate(bid, rid, "accept", iid=UUID(item["id"]), etag='"1"')
    with stores["operator"].transaction() as s:
        Operator(s, "synthetic-test-operator", "PR4").provision(bid, member)
    with app.transaction() as s:
        assert RoomService(svc(s, member)).read(rid)["headStateId"] is None
        with pytest.raises(AccessError):
            Collaboration(svc(s, member)).mutate(
                bid, rid, "leave", iid=UUID(item["id"]), etag='"2"'
            )


def test_no_direct_function_bypass_and_no_context(stores, invitation):
    a, b, aid, bid, rid, iid = invitation
    app = stores["app"]
    with app.transaction() as s:
        assert s.scalar(sa.text("SELECT count(*) FROM control_api.room_invitations")) == 0
        assert not s.scalar(sa.text("SELECT control_api.room_access(:rid)"), {"rid": rid})
        assert not s.scalar(
            sa.text("SELECT has_schema_privilege('kryptroom_auth_guard','control_api','CREATE')")
        )
    # Even calling the narrow function directly cannot forge scope/target.
    for uid, scope, action in ((b, aid, "accept"), (a, aid, "accept"), (b, bid, "revoke")):
        with pytest.raises(DBAPIError), app.transaction() as s:
            svc(s, uid)
            s.execute(
                sa.text(
                    "SELECT control_api.room_collaboration(:rid,:scope,:iid,:action,1,NULL,NULL)"
                ),
                {"rid": rid, "scope": scope, "iid": iid, "action": action},
            )


def test_event_history_exactly_once_and_app_cannot_rewrite(stores, invitation, postgres_settings):
    _, b, _, bid, rid, iid = invitation
    with stores["app"].transaction() as s:
        c = Collaboration(svc(s, b))
        c.mutate(bid, rid, "accept", iid=iid, etag='"1"')
        c.mutate(bid, rid, "accept", iid=iid, etag='"1"')
        c.mutate(bid, rid, "leave", iid=iid, etag='"2"')
        c.mutate(bid, rid, "leave", iid=iid, etag='"2"')
    db = Database(postgres_settings)
    try:
        with db.transaction() as s:
            # Trusted migration controller only; the API cannot SET ROLE to this NOLOGIN guard.
            s.execute(sa.text("SET LOCAL ROLE kryptroom_auth_guard"))
            events = s.execute(
                sa.text(
                    "SELECT kind,count(*) FROM control_api.room_collaboration_events "
                    "WHERE invitation_id=:iid GROUP BY kind"
                ),
                {"iid": iid},
            ).all()
            assert dict(events) == {"invite": 1, "accept": 1, "leave": 1}
    finally:
        db.close()
    for statement in (
        "SELECT * FROM control_api.room_collaboration_events",
        "DELETE FROM control_api.room_collaboration_events",
    ):
        with pytest.raises(DBAPIError), stores["app"].transaction() as s:
            svc(s, b)
            s.execute(sa.text(statement))


def test_authority_revoked_while_invitation_mutation_waits(stores, cohort):
    a, _, _, admin, aid, bid, _, _, membership = cohort
    app = stores["app"]
    with app.transaction() as s:
        rid = UUID(RoomService(svc(s, a)).create(aid, "Concurrent", "", str(uuid4()))["id"])
    ready, attempting = Queue(), Event()

    def worker():
        with app.transaction() as s:
            auth = svc(s, admin)
            auth.authorized(aid, BusinessAction.ORGANIZATION_UPDATE)
            ready.put(s.scalar(sa.text("SELECT pg_backend_pid()")))
            attempting.set()
            try:
                return Collaboration(auth).mutate(aid, rid, "invite", target=bid, key="forbidden")
            except AccessError as error:
                return error.code

    with ThreadPoolExecutor(max_workers=1) as pool:
        with app.transaction() as s:
            auth = svc(s, a)
            auth.authorized(aid, BusinessAction.MEMBERS_REVOKE, lock=True)
            future = pool.submit(worker)
            assert_database_blocker(s, ready, attempting)
            auth.change_member(aid, membership, None, '"1"')
        assert future.result(timeout=5) == "resource_not_found"
    with app.transaction() as s:
        assert Collaboration(svc(s, a)).listing(aid, 25, None)["items"] == []
