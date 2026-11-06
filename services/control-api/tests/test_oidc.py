"""Strict verifier unit negatives; real Keycloak is required separately for acceptance."""

import json
import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from pydantic import SecretStr

from kryptroom_control.oidc import (
    AuthenticationFailed,
    IdentityProviderUnavailable,
    OIDCConfiguration,
    OIDCVerifier,
)

ISSUER = "http://127.0.0.1:8084/realms/kryptroom-dev"


@pytest.fixture(scope="module")
def key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def client(monkeypatch, key):
    verifier = OIDCVerifier(
        OIDCConfiguration(
            ISSUER, "kryptroom-control-api", SecretStr("test-only-" + "a" * 32), local_http=True
        )
    )
    public = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key()))
    public.update(kid="trusted", use="sig", alg="RS256")
    state = {"active": True, "calls": []}

    def response(url, token=None):
        state["calls"].append(url)
        if url.endswith("openid-configuration"):
            return {
                "issuer": ISSUER,
                "jwks_uri": ISSUER + "/certs",
                "introspection_endpoint": ISSUER + "/introspect",
            }
        if url.endswith("certs"):
            return {"keys": [public]}
        return {"active": state["active"], "sub": "alice", "client_id": "kryptroom-web-bff"}

    monkeypatch.setattr(verifier, "_json", response)
    return verifier, state


def claims():
    now = int(time.time())
    return {
        "iss": ISSUER,
        "sub": "alice",
        "aud": "kryptroom-control-api",
        "azp": "kryptroom-web-bff",
        "typ": "Bearer",
        "iat": now,
        "exp": now + 300,
        "name": "Alice",
        "email": "same@example.test",
    }


def encode(key, payload=None, kid="trusted"):
    return SecretStr(jwt.encode(payload or claims(), key, algorithm="RS256", headers={"kid": kid}))


def test_valid_identity_has_no_organization_authority(client, key):
    verifier, _ = client
    identity = verifier.verify_access_token(encode(key))
    assert identity.issuer == ISSUER and identity.subject == "alice"
    assert not hasattr(identity, "role") and not hasattr(identity, "organization_id")


@pytest.mark.parametrize(
    "field,value",
    [
        ("iss", "https://untrusted.example/realm"),
        ("aud", "another-api"),
        ("sub", ""),
        ("sub", False),
        ("azp", "untrusted-client"),
        ("typ", "ID"),
        ("exp", 1),
        ("exp", False),
        ("iat", 999999999999),
        ("nbf", 999999999999),
    ],
)
def test_invalid_claims_fail_without_reflecting_token(client, key, field, value):
    payload = claims()
    payload[field] = value
    token = encode(key, payload)
    with pytest.raises(AuthenticationFailed) as error:
        client[0].verify_access_token(token)
    assert token.get_secret_value() not in str(error.value)


@pytest.mark.parametrize("field", ["iss", "sub", "aud", "exp", "iat", "azp", "typ"])
def test_missing_claims_rejected(client, key, field):
    payload = claims()
    del payload[field]
    with pytest.raises(AuthenticationFailed):
        client[0].verify_access_token(encode(key, payload))


def test_invalid_signature_rejected(client):
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with pytest.raises(AuthenticationFailed):
        client[0].verify_access_token(encode(other))


def test_none_algorithm_rejected_before_network(client):
    token = SecretStr(jwt.encode(claims(), None, algorithm="none", headers={"kid": "trusted"}))
    with pytest.raises(AuthenticationFailed):
        client[0].verify_access_token(token)
    assert not client[1]["calls"]


def test_unknown_key_has_only_one_bounded_refresh(client, key):
    with pytest.raises(AuthenticationFailed):
        client[0].verify_access_token(encode(key, kid="unknown"))
    assert len([url for url in client[1]["calls"] if url.endswith("certs")]) == 2


def test_no_positive_introspection_cache(client, key):
    token = encode(key)
    client[0].verify_access_token(token)
    client[1]["active"] = False
    with pytest.raises(AuthenticationFailed):
        client[0].verify_access_token(token)
    assert len([url for url in client[1]["calls"] if url.endswith("introspect")]) == 2


def test_provider_outage_fails_closed_even_with_cached_signing_key(client, key, monkeypatch):
    token = encode(key)
    client[0].verify_access_token(token)

    def unavailable(*args, **kwargs):
        raise IdentityProviderUnavailable()

    monkeypatch.setattr(client[0], "_json", unavailable)
    with pytest.raises(IdentityProviderUnavailable):
        client[0].verify_access_token(token)


@pytest.mark.parametrize("issuer,local", [("http://external.test/realm", True), (ISSUER, False)])
def test_external_plaintext_or_implicit_local_http_rejected(issuer, local):
    with pytest.raises(ValueError):
        OIDCConfiguration(issuer, "api", SecretStr("a" * 32), local_http=local)


def test_development_transport_does_not_relax_issuer_or_allow_arbitrary_endpoints():
    verifier = OIDCVerifier(
        OIDCConfiguration(
            ISSUER,
            "api",
            SecretStr("a" * 32),
            local_http=True,
            transport_origin="http://keycloak:8080",
        )
    )
    assert verifier._url(ISSUER + "/certs") == "http://keycloak:8080/realms/kryptroom-dev/certs"
    with pytest.raises(IdentityProviderUnavailable):
        verifier._url("https://attacker.test/steal")
