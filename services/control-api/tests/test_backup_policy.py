"""The release rehearsal must refuse unrelated databases before invoking Docker."""

import runpy
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/backup-restore-acceptance.py"


@pytest.mark.parametrize("container", ["postgres", "kr-m9-unrelated-postgres", "kr-m9-closure/a"])
def test_unrelated_container_is_refused_before_any_command(monkeypatch, container):
    def forbidden(*args, **kwargs):
        raise AssertionError("No external operation is allowed")

    monkeypatch.setattr("subprocess.run", forbidden)
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--disposable", "--container", container])
    with pytest.raises(ValueError, match="dedicated disposable"):
        runpy.run_path(str(SCRIPT))["main"]()


def test_explicit_disposable_acknowledgement_is_required(monkeypatch):
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--container", "kr-m9-closure-postgres-1"])
    with pytest.raises(SystemExit) as error:
        runpy.run_path(str(SCRIPT))["main"]()
    assert error.value.code == 2


def test_invalid_port_is_rejected_before_external_operations(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [str(SCRIPT), "--disposable", "--container", "kr-m9-closure-postgres-1", "--port", "0"],
    )
    with pytest.raises(ValueError, match="Invalid fixture port"):
        runpy.run_path(str(SCRIPT))["main"]()
