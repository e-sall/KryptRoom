"""Public metadata contracts and default-deny boundary; acceptance uses a real IdP."""

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from kryptroom_control.app import create_app
from kryptroom_control.identity_api import EmptyInput, OrganizationInput, RoleInput
from kryptroom_control.organization_service import AccessError, require_version


def test_configured_openapi_has_exact_metadata_scope_and_bearer(settings, tmp_path: Path):
    secret = tmp_path / "synthetic-oidc-credential"
    secret.write_text("synthetic-oidc-client-credential-0123456789")
    app = create_app(
        settings.model_copy(
            update={
                "oidc_issuer": "https://issuer.example.test/realm",
                "oidc_client_secret_file": secret,
            }
        )
    )
    schema = app.openapi()
    paths = schema["paths"]
    assert set(paths) == {
        "/health/live",
        "/health/ready",
        "/api/v1/auth/complete",
        "/api/v1/me",
        "/api/v1/me/registrations",
        "/api/v1/organizations",
        "/api/v1/organizations/{organizationId}",
        "/api/v1/organizations/{organizationId}/members",
        "/api/v1/organizations/{organizationId}/members/{membershipId}",
        "/api/v1/organizations/{organizationId}/rooms",
        "/api/v1/rooms/{roomId}",
    }
    assert schema["components"]["securitySchemes"]["HTTPBearer"]["scheme"] == "bearer"
    assert set(paths["/api/v1/organizations/{organizationId}/members"]) == {"get"}
    with TestClient(app) as client:
        assert client.get("/health/live").status_code == 200
        for method, path in [
            ("get", "/api/v1/me"),
            ("post", "/api/v1/auth/complete"),
            ("get", f"/api/v1/organizations/{uuid4()}"),
        ]:
            response = getattr(client, method)(path)
            assert response.status_code == 401
            assert response.headers["cache-control"] == "private, no-store"
            assert response.json()["error"]["code"] == "authentication_required"
        for forbidden in ("/run", "/reveal", "/decrypt", "/prove", "/anchor", "/api/v1/rooms"):
            assert client.post(forbidden).status_code == 404


@pytest.mark.parametrize(
    "body",
    [
        {"displayName": ""},
        {"displayName": " "},
        {"displayName": "invalid\x00label"},
        {"displayName": "x" * 121},
        {"displayName": "Synthetic", "status": "ACTIVE"},
        {"displayName": "Synthetic", "created_by": str(uuid4())},
        {"displayName": "Synthetic", "approved_by": str(uuid4())},
        {"displayName": "Synthetic", "role": "ORG_OWNER"},
    ],
)
def test_registration_cannot_supply_authority(body):
    with pytest.raises(ValidationError):
        OrganizationInput.model_validate(body)


def test_role_and_auth_complete_strict_extra_fields():
    for body in ({"role": "ROOT"}, {"role": "ORG_OWNER", "status": "ACTIVE"}):
        with pytest.raises(ValidationError):
            RoleInput.model_validate(body)
    with pytest.raises(ValidationError):
        EmptyInput.model_validate({"organization_id": str(uuid4())})


@pytest.mark.parametrize("etag,status", [(None, 428), ('W/"1"', 412), ('"0"', 412), ("*", 412)])
def test_mutations_require_exact_strong_version(etag, status):
    with pytest.raises(AccessError) as error:
        require_version(etag, 1)
    assert error.value.status == status
    require_version('"1"', 1)
