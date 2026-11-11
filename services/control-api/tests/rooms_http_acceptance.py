"""Loopback-only PR3 acceptance using real Keycloak PKCE, API and PostgreSQL.

Run in the trusted synthetic fixture controller, never a browser or production.
No token, password or joined dataset is printed or written as evidence.
"""

import base64
import hashlib
import http.cookiejar
import json
import secrets
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from uuid import UUID

from pydantic import SecretStr

from kryptroom_control.config import Settings
from kryptroom_control.db import Database
from kryptroom_control.operator import Operator

ROOT = Path(__file__).resolve().parents[1]
ISSUER = "https://127.0.0.1:8444/realms/kryptroom-dev"
API = "http://127.0.0.1:8001/api/v1"
CALLBACK = "http://127.0.0.1:3004/auth/callback"
TLS = ssl.create_default_context(cafile=str(ROOT / ".runtime/identity/tls/ca.crt"))


class Callback(Exception):
    def __init__(self, url):
        self.url = url


class Redirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        if newurl.startswith(CALLBACK + "?"):
            raise Callback(newurl)
        if not newurl.startswith(ISSUER + "/"):
            raise RuntimeError("Unexpected fixture redirect")
        return super().redirect_request(request, fp, code, message, headers, newurl)


class Form(HTMLParser):
    action = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "form" and attrs.get("id") == "kc-form-login":
            self.action = attrs.get("action")


def secret(name):
    return (ROOT / ".runtime/secrets" / name).read_text()


def login(user):
    verifier, state = secrets.token_urlsafe(48), secrets.token_urlsafe(32)
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    )
    query = urllib.parse.urlencode(
        {
            "client_id": "kryptroom-web-bff",
            "redirect_uri": CALLBACK,
            "response_type": "code",
            "scope": "openid profile email",
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
    )
    browser = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
        urllib.request.HTTPSHandler(context=TLS),
        Redirect(),
    )
    with browser.open(ISSUER + "/protocol/openid-connect/auth?" + query, timeout=10) as result:
        form = Form()
        form.feed(result.read().decode())
    if not form.action or not form.action.startswith(ISSUER + "/"):
        raise RuntimeError("Expected actual Keycloak form")
    try:
        browser.open(
            urllib.request.Request(  # noqa: S310 — form action checked against fixed HTTPS issuer
                form.action,
                data=urllib.parse.urlencode(
                    {"username": user, "password": secret(user + "_password"), "credentialId": ""}
                ).encode(),
            ),
            timeout=10,
        ).close()
    except Callback as callback:
        fields = urllib.parse.parse_qs(urllib.parse.urlsplit(callback.url).query)
        if fields.get("state") != [state] or "code" not in fields:
            raise RuntimeError("Invalid authorization state") from None
        pair = base64.b64encode(
            ("kryptroom-web-bff:" + secret("oidc_bff_secret")).encode()
        ).decode()
        request = urllib.request.Request(  # noqa: S310 — fixed loopback HTTPS issuer
            ISSUER + "/protocol/openid-connect/token",
            data=urllib.parse.urlencode(
                {
                    "grant_type": "authorization_code",
                    "code": fields["code"][0],
                    "redirect_uri": CALLBACK,
                    "code_verifier": verifier,
                }
            ).encode(),
            headers={"Authorization": "Basic " + pair},
        )
        with urllib.request.urlopen(request, context=TLS, timeout=10) as result:  # noqa: S310
            return json.load(result)
    raise RuntimeError("Real login did not return an authorization code")


def call(method, path, token=None, body=None, **headers):
    if token:
        headers["Authorization"] = "Bearer " + token
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(  # noqa: S310 — fixed loopback API prefix, no arbitrary URLs
        API + path,
        method=method,
        headers=headers,
        data=json.dumps(body).encode() if body is not None else None,
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310
            return response.status, json.load(response), response.headers
    except urllib.error.HTTPError as error:
        return error.code, json.load(error), error.headers


def main():
    if "--reload" in sys.argv:
        reference = json.loads((ROOT / ".runtime/pr3-room-reference.json").read_text())
        token = login("alice")["access_token"]
        status, body, _ = call("GET", "/rooms/" + reference["id"], token)
        assert status == 200
        assert body["data"]["version"] == reference["version"]
        assert body["data"]["displayName"] == "New"
        assert body["data"]["headStateId"] is None
        print(
            json.dumps({"fresh_process_after_api_restart": True, "persistent_room_verified": True})
        )
        return
    alice, bob = login("alice"), login("bob")
    a, b = alice["access_token"], bob["access_token"]
    for token in (a, b):
        assert call("POST", "/auth/complete", token, {})[0] == 200
    organizations = []
    for token in (a, b):
        status, body, _ = call(
            "POST",
            "/organizations",
            token,
            {"displayName": "Synthetic PR3"},
            **{"Idempotency-Key": secrets.token_hex(16)},
        )
        assert status == 202
        organizations.append(body["data"]["id"])
    settings = Settings(
        database_host="127.0.0.1",
        database_port=5435,
        database_user="kryptroom_operator",
        database_password=SecretStr(secret("operator_password")),
        database_sslmode="disable",
    )
    db = Database(settings)
    try:
        for oid in organizations:
            with db.transaction() as session:
                Operator(session, "synthetic-pr3-controller", "PR3-ACCEPTANCE").approve(UUID(oid))
    finally:
        db.close()
    path = "/organizations/" + organizations[0] + "/rooms"
    key = secrets.token_hex(16)
    payload = {"displayName": "Persistent synthetic room", "description": "Metadata only"}
    status, body, headers = call("POST", path, a, payload, **{"Idempotency-Key": key})
    assert status == 201 and headers["ETag"] == '"1"'
    room = body["data"]
    rid = room["id"]
    assert room["headStateId"] is None
    assert call("POST", path, a, payload, **{"Idempotency-Key": key})[1]["data"] == room
    assert call("POST", path, a, {"displayName": "Conflict"}, **{"Idempotency-Key": key})[0] == 409
    assert call("GET", "/rooms/" + rid)[0] == 401
    assert call("GET", "/rooms/" + rid, b)[0] == 404
    assert call("POST", path, b, payload, **{"Idempotency-Key": key})[0] == 404
    assert (
        call("PATCH", "/rooms/" + rid, b, {"displayName": "Forbidden"}, **{"If-Match": '"1"'})[0]
        == 404
    )
    assert call("PATCH", "/rooms/" + rid, a, {"displayName": "New"})[0] == 428
    assert (
        call("PATCH", "/rooms/" + rid, a, {"displayName": "New"}, **{"If-Match": '"9"'})[0] == 412
    )
    assert (
        call("PATCH", "/rooms/" + rid, a, {"displayName": "New"}, **{"If-Match": '"1"'})[0] == 200
    )
    assert (
        call("PATCH", "/rooms/" + rid, a, {"headStateId": str(UUID(int=1))}, **{"If-Match": '"2"'})[
            0
        ]
        == 422
    )
    assert call("GET", "/rooms/" + rid, a)[1]["data"]["displayName"] == "New"
    assert call("GET", path, a)[1]["data"]["items"][0]["id"] == rid
    # Keep only synthetic identifiers, not tokens, for a fresh-process reload probe.
    (ROOT / ".runtime/pr3-room-reference.json").write_text(json.dumps({"id": rid, "version": 2}))
    request = urllib.request.Request(  # noqa: S310 — fixed HTTPS loopback issuer
        ISSUER + "/protocol/openid-connect/logout",
        data=urllib.parse.urlencode(
            {
                "client_id": "kryptroom-web-bff",
                "client_secret": secret("oidc_bff_secret"),
                "refresh_token": alice["refresh_token"],
            }
        ).encode(),
    )
    with urllib.request.urlopen(request, context=TLS, timeout=10) as result:  # noqa: S310
        assert result.status == 204
    assert call("GET", "/rooms/" + rid, a)[0] == 401
    print(
        json.dumps(
            {
                "real_keycloak_pkce": True,
                "api_authorization": True,
                "cross_tenant_refused": True,
                "idempotency": True,
                "if_match": True,
                "head_state_null": True,
                "inactive_token_introspection_rejected": True,
            }
        )
    )


if __name__ == "__main__":
    main()
