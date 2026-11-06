import json
import logging
import socket
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr, ValidationError

from kryptroom_control.app import create_app
from kryptroom_control.config import Settings, load_settings
from kryptroom_control.contracts import BusinessError, Page, PageRequest
from kryptroom_control.modules.authorization import (
    BusinessAction,
    DenyAllAuthorizer,
    ResourceScope,
)
from kryptroom_control.modules.identity import Principal


def test_live_does_not_connect_and_ready_really_fails(settings: Settings) -> None:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
        # Bound but not listening: PostgreSQL is actually unavailable at this port.
        app = create_app(settings.model_copy(update={"database_port": port}))
        with TestClient(app) as client:
            assert client.get("/health/live").json() == {"status": "alive"}
            response = client.get("/health/ready")
            assert response.status_code == 503
            assert response.json()["error"]["code"] == "not_ready"
            assert response.json()["correlation_id"] == response.headers["x-correlation-id"]
            assert "password" not in response.text.lower()


def test_openapi_exact_scope_and_disabled_by_default(settings: Settings) -> None:
    app = create_app(settings)
    assert app.openapi()["openapi"].startswith("3.1.")
    assert set(app.openapi()["paths"]) == {"/health/live", "/health/ready"}
    assert not app.debug
    with TestClient(app) as client:
        for path in (
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/rooms",
            "/me",
            "/run",
            "/reveal",
            "/decrypt",
            "/prove",
            "/anchor",
        ):
            assert client.get(path).status_code == 404
            assert client.post(path, json={"secret": "do-not-reflect"}).status_code == 404
    with TestClient(create_app(settings.model_copy(update={"docs_enabled": True}))) as client:
        schema = client.get("/openapi.json").json()
        assert schema["openapi"].startswith("3.1.")
        assert "securitySchemes" not in schema["components"]


def test_correlation_is_server_generated_and_logs_are_allowlisted(
    settings: Settings,
    caplog: pytest.LogCaptureFixture,
) -> None:
    secret = "DO-NOT-LOG-REQUEST-TOKEN"  # noqa: S105 — deliberate public leakage sentinel
    with (
        TestClient(create_app(settings)) as client,
        caplog.at_level(logging.INFO, logger="kryptroom_control.http"),
    ):
        responses = [
            client.get(
                "/" + secret + "?token=" + secret,
                headers={"Authorization": "Bearer " + secret, "X-Correlation-ID": secret},
            ),
            client.get("/health/live"),
        ]
    ids = [UUID(response.headers["x-correlation-id"]) for response in responses]
    assert all(value.version == 4 for value in ids)
    assert ids[0] != ids[1]
    logs = [record.message for record in caplog.records if record.name == "kryptroom_control.http"]
    assert len(logs) == 2
    assert secret not in " ".join(logs)
    assert json.loads(logs[0])["route"] == "unmatched"
    assert all(response.headers["cache-control"] == "no-store" for response in responses)


def add_failure_routes(app: FastAPI) -> None:
    @app.get("/_test/failure")
    def fail() -> None:
        raise RuntimeError("credential-DO-NOT-LEAK")

    @app.get("/_test/validation")
    def invalid(value: int) -> int:
        return value

    @app.get("/_test/denied")
    def denied() -> None:
        raise BusinessError("permission_denied")


@pytest.mark.parametrize(
    "route,status,code",
    [
        ("/_test/failure", 500, "internal_error"),
        ("/_test/validation?value=credential-DO-NOT-LEAK", 422, "validation_error"),
        ("/_test/denied", 403, "permission_denied"),
        ("/health/live", 405, "http_error"),
    ],
)
def test_error_contract_redacts_input_and_exception(
    settings: Settings,
    caplog: pytest.LogCaptureFixture,
    route: str,
    status: int,
    code: str,
) -> None:
    app = create_app(settings)
    add_failure_routes(app)
    with TestClient(app) as client, caplog.at_level(logging.INFO, logger="kryptroom_control.http"):
        response = client.post(route) if status == 405 else client.get(route)
    assert response.status_code == status
    assert response.json()["error"]["code"] == code
    assert response.json()["correlation_id"] == response.headers["x-correlation-id"]
    assert "credential-DO-NOT-LEAK" not in response.text
    assert "credential-DO-NOT-LEAK" not in " ".join(
        r.message for r in caplog.records if r.name.startswith("kryptroom_control")
    )


@pytest.mark.parametrize("action", list(BusinessAction))
def test_business_authorization_denies_by_default(action: BusinessAction) -> None:
    with pytest.raises(BusinessError, match="permission_denied"):
        DenyAllAuthorizer().require(Principal(uuid4()), action, ResourceScope(uuid4(), uuid4()))


@pytest.mark.parametrize(
    "values",
    [
        {"limit": 0},
        {"limit": 101},
        {"cursor": "x" * 513},
        {"untrusted": "extra"},
    ],
)
def test_pagination_is_bounded(values: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        PageRequest(**values)


def test_pagination_is_immutable() -> None:
    page = Page[str](items=("metadata-id",))
    with pytest.raises(ValidationError):
        page.next_cursor = "other"


def test_settings_redact_and_reject_uncontrolled_registration(
    settings: Settings,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "sensitive-test-credential-0123456789"  # noqa: S105 — synthetic test input
    path = tmp_path / "credential"
    path.write_text(secret)
    data = settings.model_dump(exclude={"database_password", "database_password_file"})
    value = Settings(**data, database_password_file=path)
    assert secret not in repr(value)
    assert secret not in repr(value.database_url())
    assert secret not in value.model_dump_json()
    with pytest.raises(ValidationError):
        Settings(**data, database_password=SecretStr(secret), database_password_file=path)
    with pytest.raises(ValidationError):
        Settings(database_password=SecretStr(secret), organization_registration="self-service")
    monkeypatch.setenv("CONTROL_DATABASE_PASSWORD", "too-short-secret")
    with pytest.raises(RuntimeError) as exc:
        load_settings()
    assert "too-short-secret" not in str(exc.value)


def test_m9_has_no_core_import_or_crypto_api() -> None:
    import ast

    root = Path(__file__).resolve().parents[1] / "src"
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                imports = [node.module or ""]
            else:
                continue
            assert not any(
                name.split(".")[0] in {"engines", "nodes", "secretflow", "spu", "openfhe", "web3"}
                for name in imports
            ), path
