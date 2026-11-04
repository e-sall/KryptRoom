import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic import SecretStr

from kryptroom_control.config import Settings


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    # Unit inputs must not inherit credentials or target databases from an integration shell.
    for name in tuple(os.environ):
        if name.startswith("CONTROL_"):
            monkeypatch.delenv(name)
    return Settings(
        environment="test",
        database_password=SecretStr("synthetic-test-password-only-0123456789"),
        database_sslmode="disable",
        database_port=1,
    )


@pytest.fixture(scope="session")
def postgres_settings() -> Iterator[Settings]:
    # Unit-only runs must explicitly exclude this marker. A selected integration run
    # fails instead of silently skipping if its database configuration is absent.
    if os.environ.get("CONTROL_TEST_POSTGRES") != "1":
        pytest.fail("Set CONTROL_TEST_POSTGRES=1 and configure an isolated *_test database")
    settings = Settings()
    if not settings.database_name.endswith("_test") or settings.environment != "test":
        pytest.fail("Integration requires CONTROL_ENVIRONMENT=test and a *_test database")
    yield settings


@pytest.fixture(scope="session")
def app_password() -> SecretStr:
    path = os.environ.get("CONTROL_TEST_APP_PASSWORD_FILE")
    if not path:
        pytest.fail("Configure the separate application-role password file")
    return SecretStr(Path(path).read_text(encoding="utf-8").rstrip("\r\n"))
