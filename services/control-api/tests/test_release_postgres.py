"""Release policy must protect actual history, not just a configuration flag."""

from pathlib import Path
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from test_collaboration_postgres import svc
from test_identity_postgres import cohort as cohort
from test_identity_postgres import stores as stores

from kryptroom_control.collaboration import Collaboration
from kryptroom_control.room_service import RoomService

pytestmark = pytest.mark.postgres


def test_default_downgrade_preserves_rows_version_and_history(stores, cohort):
    a, _, _, _, aid, bid, *_ = cohort
    with stores["app"].transaction() as s:
        auth = svc(s, a)
        room = RoomService(auth).create(aid, "Restore acceptance synthetic", "", str(uuid4()))
        rid = UUID(room["id"])
        Collaboration(auth).mutate(aid, rid, "invite", target=bid, key="release")
        history = Collaboration(auth).history(rid, 100, None)
        assert len(history["items"]) == 2
    c = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    with pytest.raises(RuntimeError, match="History-losing downgrade blocked"):
        command.downgrade(c, "0005_action_guard")
    with stores["app"].transaction() as s:
        assert RoomService(svc(s, a)).read(rid) == room
        assert Collaboration(svc(s, a)).history(rid, 100, None) == history
        assert (
            s.scalar(sa.text("SELECT version_num FROM control_api.alembic_version"))
            == "0006_room_history"
        )
    print("PASS refused destructive downgrade before DDL; Room/history/schema version unchanged")
