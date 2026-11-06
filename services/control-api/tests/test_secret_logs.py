"""QA04-01: full-cycle leak detection and bounded, redacted diagnostics."""

import importlib.util
import subprocess
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "compose_acceptance", Path(__file__).resolve().parents[1] / "scripts/compose-acceptance.py"
)
assert SPEC is not None and SPEC.loader is not None
acceptance = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(acceptance)


def test_early_credential_is_detected_after_more_than_200_lines(monkeypatch, capsys) -> None:
    sentinel = "synthetic-credential-sentinel-qa04"
    lines = [sentinel, *[f"ordinary line {i}" for i in range(250)]]
    calls = []

    def logs(arguments, **kwargs):
        calls.append(arguments)
        payload = "\n".join(lines[-200:] if "--tail" in arguments else lines)
        return subprocess.CompletedProcess(arguments, 0, payload, "")

    monkeypatch.setattr(acceptance.subprocess, "run", logs)
    with pytest.raises(AssertionError, match="A local credential appeared") as error:
        acceptance.assert_no_credentials(acceptance.container_logs(), [sentinel])
    assert "--tail" not in calls[0]
    assert sentinel not in str(error.value)
    output = capsys.readouterr()
    assert sentinel not in output.out + output.err
    assert len(acceptance.container_logs(diagnostic=True).splitlines()) == 200
    assert calls[1][-2:] == ["--tail", "200"]


def test_stderr_is_included_in_confidentiality_scan(monkeypatch) -> None:
    sentinel = "synthetic-stderr-credential-qa04"
    monkeypatch.setattr(
        acceptance.subprocess,
        "run",
        lambda arguments, **kwargs: subprocess.CompletedProcess(arguments, 0, "ordinary", sentinel),
    )
    with pytest.raises(AssertionError, match="A local credential appeared"):
        acceptance.assert_no_credentials(acceptance.container_logs(), [sentinel])


def test_main_failure_only_displays_bounded_redacted_diagnostics(monkeypatch, capsys) -> None:
    sentinel = "synthetic-credential-diagnostic-qa04"
    modes = []

    def logs(*, diagnostic=False):
        modes.append(diagnostic)
        return sentinel + "\n" + "ordinary line\n" * (10 if diagnostic else 250)

    monkeypatch.setattr(acceptance, "docker", "unused-local-test-docker")
    monkeypatch.setattr(acceptance, "compose", lambda *args: None)
    monkeypatch.setattr(acceptance, "expect", lambda status: None)
    monkeypatch.setattr(acceptance, "credentials", lambda: [sentinel])
    monkeypatch.setattr(acceptance, "container_logs", logs)
    monkeypatch.setattr(acceptance.subprocess, "run", lambda *args, **kwargs: None)
    with pytest.raises(AssertionError, match="A local credential appeared"):
        acceptance.main()
    output = capsys.readouterr()
    assert modes == [False, True]
    assert sentinel not in output.out + output.err
    assert "[REDACTED-LOCAL-CREDENTIAL]" in output.err
    assert '"credential_log_scan": "passed"' not in output.out
