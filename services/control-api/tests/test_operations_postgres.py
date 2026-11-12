"""PR5 native PostgreSQL upgrades and narrowly visible business history."""

import hashlib
import os
from pathlib import Path
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from pydantic import SecretStr
from sqlalchemy.exc import DBAPIError
from test_collaboration_postgres import svc
from test_identity_postgres import approve, register, resolve
from test_identity_postgres import cohort as cohort
from test_identity_postgres import stores as stores

from kryptroom_control.collaboration import Collaboration
from kryptroom_control.db import Database
from kryptroom_control.organization_service import AccessError
from kryptroom_control.room_service import RoomService

pytestmark = pytest.mark.postgres
ROOT = Path(__file__).resolve().parents[1]


def config():
    result = Config(str(ROOT / "alembic.ini"))
    result.attributes["allow_disposable_history_loss"] = True
    return result


def snapshot(db):
    with db.transaction() as s:
        s.execute(sa.text("SET LOCAL ROLE kryptroom_auth_guard"))
        rows = {
            table: s.scalars(
                sa.text(
                    f"SELECT to_jsonb(t) FROM control_api.{table} t ORDER BY id"  # noqa: S608
                )
            ).all()
            for table in ("rooms", "room_invitations", "room_collaboration_events")
        }
        acl = s.execute(
            sa.text("""SELECT proowner,proacl,prosecdef,proconfig FROM pg_proc
            WHERE oid=('control_api.room_collaboration'
            ||'(uuid,uuid,uuid,text,integer,uuid,text)')::regprocedure""")
        ).one()
        return rows, acl


def test_legacy_0004_upgrade_preserves_data_owner_acl(postgres_settings, app_password):
    command.downgrade(config(), "base")
    command.upgrade(config(), "0004_collaboration")
    db = Database(postgres_settings)
    legacy = (ROOT / "tests/fixtures/0004-legacy-collaboration.sql").read_text()
    assert hashlib.sha256(legacy.encode()).hexdigest() == (
        "cb388b6ebf4cedf716bcc340cb612b5a1819a4ebed3721cdff5bb05141e4a910"
    )
    with db.transaction() as s:
        s.execute(sa.text(legacy))
        assert not s.scalar(
            sa.text("""SELECT position('IF action IS NULL OR action NOT IN' in prosrc)>0
            FROM pg_proc WHERE oid=('control_api.room_collaboration'
            ||'(uuid,uuid,uuid,text,integer,uuid,text)')::regprocedure""")
        )
    app = Database(
        postgres_settings.model_copy(
            update={
                "database_user": "kryptroom_app",
                "database_password": app_password,
                "database_password_file": None,
            }
        )
    )
    operator = Database(
        postgres_settings.model_copy(
            update={
                "database_user": "kryptroom_operator",
                "database_password": SecretStr(
                    Path(os.environ["CONTROL_TEST_OPERATOR_PASSWORD_FILE"]).read_text()
                ),
                "database_password_file": None,
            }
        )
    )
    try:
        a, b = resolve(app, str(uuid4())), resolve(app, str(uuid4()))
        aid, bid = UUID(register(app, a)["id"]), UUID(register(app, b)["id"])
        approve(operator, aid)
        approve(operator, bid)
        for state in ("PENDING", "ACCEPTED", "REVOKED"):
            with app.transaction() as s:
                auth = svc(s, a)
                rid = UUID(
                    RoomService(auth).create(aid, "Upgrade synthetic", "", str(uuid4()))["id"]
                )
                item = Collaboration(auth).mutate(aid, rid, "invite", target=bid, key=str(uuid4()))
            if state != "PENDING":
                with app.transaction() as s:
                    Collaboration(svc(s, b) if state == "ACCEPTED" else svc(s, a)).mutate(
                        bid if state == "ACCEPTED" else aid,
                        rid,
                        "accept" if state == "ACCEPTED" else "revoke",
                        iid=UUID(item["id"]),
                        etag='"1"',
                    )
        before = snapshot(db)
        command.upgrade(config(), "0005_action_guard")
        assert snapshot(db) == before
        with app.transaction() as s:
            svc(s, a)
            for action in (None, "unknown"):
                with pytest.raises(DBAPIError) as error, s.begin_nested():
                    s.execute(
                        sa.text("SELECT control_api.room_collaboration(:r,:o,:i,:a,2,NULL,NULL)"),
                        {"r": rid, "o": aid, "i": UUID(item["id"]), "a": action},
                    )
                assert error.value.orig.sqlstate == "22023"
        command.upgrade(config(), "head")
        command.upgrade(config(), "head")
        assert snapshot(db) == before
        with db.transaction() as s:
            s.execute(sa.text("SET LOCAL ROLE kryptroom_auth_guard"))
            assert s.scalar(
                sa.text("SELECT count(*) FROM control_api.room_operational_events")
            ) == len(before[0]["room_collaboration_events"])
        command.downgrade(config(), "0004_collaboration")
        assert snapshot(db) == before
        with db.transaction() as s:
            assert s.scalar(
                sa.text("""SELECT position('IF action IS NULL OR action NOT IN' in prosrc)>0
                FROM pg_proc WHERE oid=('control_api.room_collaboration'
                ||'(uuid,uuid,uuid,text,integer,uuid,text)')::regprocedure""")
            )
        command.upgrade(config(), "head")
        print(
            "PASS legacy 0004 -> 0005 -> head: data/ACL/owner unchanged; retries and safe downgrade"
        )
    finally:
        app.close()
        operator.close()
        db.close()


def test_fresh_install_head(postgres_settings):
    command.downgrade(config(), "base")
    command.upgrade(config(), "head")
    command.upgrade(config(), "head")
    command.check(config())
    db = Database(postgres_settings)
    try:
        assert db.ready()
    finally:
        db.close()
    print("PASS fresh PostgreSQL schema and readiness")


def test_history_scope_transactions_and_revocation(stores, cohort):
    a, b, member, _, aid, bid, *_ = cohort
    app = stores["app"]
    c = resolve(app, str(uuid4()))
    cid = UUID(register(app, c)["id"])
    approve(stores["operator"], cid)
    with app.transaction() as s:
        auth = svc(s, a)
        rid = UUID(
            RoomService(auth).create(aid, "Private business label", "No audit body", str(uuid4()))[
                "id"
            ]
        )
        RoomService(auth).update(rid, {"description": "Never in history"}, '"1"')
        item = Collaboration(auth).mutate(aid, rid, "invite", target=cid, key="old")
    with app.transaction() as s:
        Collaboration(svc(s, c)).mutate(cid, rid, "reject", iid=UUID(item["id"]), etag='"1"')
    with app.transaction() as s:
        item = Collaboration(svc(s, a)).mutate(aid, rid, "invite", target=bid, key="current")
    for user in (b, c, member):
        with app.transaction() as s:
            with pytest.raises(AccessError):
                Collaboration(svc(s, user)).history(rid, 25, None)
    with app.transaction() as s:
        Collaboration(svc(s, b)).mutate(bid, rid, "accept", iid=UUID(item["id"]), etag='"1"')
        history = Collaboration(svc(s, b)).history(rid, 25, None)["items"]
        assert {e["kind"] for e in history} == {"invitation_accept"}
        assert all(set(e) == {"id", "kind", "actorOrganizationId", "createdAt"} for e in history)
        assert str(cid) not in str(history) and "Never in history" not in str(history)
    with app.transaction() as s:
        owner = Collaboration(svc(s, a))
        first = owner.history(rid, 1, None)
        assert len(first["items"]) == 1 and first["next_cursor"]
        rest = owner.history(rid, 100, UUID(first["next_cursor"]))
        before = first["items"] + rest["items"]
        assert len(before) == 6
    with pytest.raises(RuntimeError), app.transaction() as s:
        RoomService(svc(s, a)).update(rid, {"description": "Rolled back"}, '"2"')
        raise RuntimeError("Synthetic rollback")
    with app.transaction() as s:
        owner = Collaboration(svc(s, a))
        assert owner.history(rid, 100, None)["items"] == before
        owner.mutate(aid, rid, "revoke", iid=UUID(item["id"]), etag='"2"')
    with app.transaction() as s:
        with pytest.raises(AccessError):
            Collaboration(svc(s, b)).history(rid, 25, None)
    for statement in (
        "SELECT * FROM control_api.room_operational_events",
        "DELETE FROM control_api.room_operational_events",
    ):
        with pytest.raises(DBAPIError), app.transaction() as s:
            svc(s, a)
            s.execute(sa.text(statement))
    print("PASS history owner/partner/member/C scope, redaction, atomic rollback and revocation")
