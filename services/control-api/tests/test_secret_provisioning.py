"""Private credential policy; real UID/mount/bootstrap cases run in native acceptance."""

import importlib.util
import os
import stat
from pathlib import Path
from types import SimpleNamespace

import pytest

spec = importlib.util.spec_from_file_location(
    "secret_policy", Path(__file__).resolve().parents[1] / "scripts/prepare-secrets.py"
)
assert spec is not None and spec.loader is not None
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


@pytest.mark.parametrize("value", [b"A" * 24, b"url_safe-0123456789_ABCDEF", b"B" * 128])
def test_local_credential_bounds(value: bytes) -> None:
    assert policy.validate_content(value) == value


@pytest.mark.parametrize(
    "value", [b"", b"short", b"x" * 129, b"x" * 30 + b"\n", b"x" * 30 + b"'", b"x" * 30 + b"\0"]
)
def test_bad_content_is_rejected_without_echo(value: bytes) -> None:
    with pytest.raises(policy.SecretPolicyError) as error:
        policy.validate_content(value)
    assert "Invalid local credential content" == str(error.value)


def metadata(**changes: int) -> os.stat_result:
    fields = {
        "st_mode": stat.S_IFREG | 0o600,
        "st_uid": 1001,
        "st_nlink": 1,
        "st_size": 48,
    }
    fields.update(changes)
    return SimpleNamespace(**fields)  # type: ignore[return-value]


def test_private_source_and_owner_only_projection() -> None:
    policy.validate_file(metadata(), 0o600)
    policy.validate_file(metadata(st_mode=stat.S_IFREG | 0o400, st_uid=10001), 0o400, 10001)


@pytest.mark.parametrize(
    "changes",
    [
        {"st_mode": stat.S_IFREG | 0o640},
        {"st_mode": stat.S_IFREG | 0o644},
        {"st_mode": stat.S_IFREG | 0o777},
        {"st_mode": stat.S_IFREG},
        {"st_mode": stat.S_IFLNK | 0o600},
        {"st_nlink": 2},
        {"st_size": 0},
        {"st_size": 129},
    ],
)
def test_invalid_source_metadata_fails_closed(changes: dict[str, int]) -> None:
    with pytest.raises(policy.SecretPolicyError):
        policy.validate_file(metadata(**changes), 0o600)


def test_wrong_projection_owner_or_mode_is_rejected() -> None:
    with pytest.raises(policy.SecretPolicyError):
        policy.validate_file(metadata(st_mode=stat.S_IFREG | 0o400), 0o400, 10001)
    with pytest.raises(policy.SecretPolicyError):
        policy.validate_file(metadata(st_uid=10001), 0o400, 10001)
