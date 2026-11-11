"""Wire restrictions; real PostgreSQL and Keycloak acceptance are separate tests."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from kryptroom_control.app import create_app
from kryptroom_control.room_api import RoomInput, RoomPatch


def test_room_inputs_never_accept_state_authority():
    assert RoomInput(displayName=" Synthetic Room ").displayName == "Synthetic Room"
    for values in (
        {"displayName": ""},
        {"displayName": "x", "headStateId": "fake"},
        {"displayName": "x", "organizationId": "client-claim"},
        {"displayName": "x", "status": "ACTIVE"},
        {"displayName": "x\x00"},
    ):
        with pytest.raises(ValidationError):
            RoomInput(**values)
    with pytest.raises(ValidationError):
        RoomPatch(headStateId="fake")


def test_room_routes_only_exist_with_configured_identity(settings, tmp_path: Path):
    assert not any("/rooms" in p for p in create_app(settings).openapi()["paths"])
    credential = tmp_path / "synthetic-client-secret"
    credential.write_text("synthetic-client-credential-0123456789")
    configured = settings.model_copy(
        update={
            "oidc_issuer": "https://issuer.example.test/realm",
            "oidc_client_secret_file": credential,
        }
    )
    schema = create_app(configured).openapi()
    for path in ("/api/v1/rooms/{roomId}", "/api/v1/organizations/{organizationId}/rooms"):
        for operation in schema["paths"][path].values():
            assert operation["security"] == [{"HTTPBearer": []}]
    assert (
        schema["components"]["schemas"]["RoomOutput"]["properties"]["headStateId"]["type"] == "null"
    )
