"""Actual Keycloak Authorization Code + PKCE proof; never logs returned tokens."""

import base64
import hashlib
import http.cookiejar
import json
import os
import secrets
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

import jwt
from pydantic import SecretStr

from kryptroom_control.oidc import OIDCConfiguration, OIDCVerifier

ISSUER = "https://127.0.0.1:8444/realms/kryptroom-dev"
CALLBACK = "http://127.0.0.1:3004/auth/callback"
values = json.loads(Path(os.environ["OIDC_TEST_VALUES_FILE"]).read_text())


class Callback(Exception):
    def __init__(self, url: str):
        super().__init__("Loopback callback received")
        self.url = url


class Redirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        if newurl.startswith(CALLBACK + "?"):
            raise Callback(newurl)
        if not newurl.startswith(ISSUER + "/"):
            raise AssertionError("Unexpected identity redirect")
        return super().redirect_request(request, fp, code, message, headers, newurl)


class LoginForm(HTMLParser):
    action: str | None = None
    error_text = ""
    collecting_error = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "form" and attrs.get("id") == "kc-form-login":
            self.action = attrs.get("action")
        if "kc-feedback-text" in attrs.get("class", ""):
            self.collecting_error = True

    def handle_data(self, data):
        if self.collecting_error:
            self.error_text += data

    def handle_endtag(self, tag):
        if tag == "span":
            self.collecting_error = False


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def authorization_code():
    verifier = secrets.token_urlsafe(48)
    state, nonce = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
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
            "nonce": nonce,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
    )
    browser = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()), Redirect()
    )
    with browser.open(ISSUER + "/protocol/openid-connect/auth?" + query, timeout=5) as response:
        parser = LoginForm()
        parser.feed(response.read().decode())
    require(
        parser.action is not None and parser.action.startswith(ISSUER + "/"),
        "Expected real Keycloak login form",
    )
    data = urllib.parse.urlencode(
        {"username": "alice", "password": values["KR_ALICE_PASSWORD"], "credentialId": ""}
    ).encode()
    try:
        request = urllib.request.Request(  # noqa: S310 — parsed form is checked against fixed issuer
            parser.action,
            data=data,
            headers={
                "Origin": "https://127.0.0.1:8444",
                "Referer": ISSUER + "/protocol/openid-connect/auth?" + query,
            },
        )
        browser.open(request, timeout=5).close()
    except Callback as callback:
        fields = urllib.parse.parse_qs(urllib.parse.urlsplit(callback.url).query)
        require(
            fields.get("state") == [state] and "code" in fields, "Invalid authorization response"
        )
        return fields["code"][0], verifier, nonce
    except urllib.error.HTTPError as error:
        diagnostic = LoginForm()
        body = error.read(8192).decode(errors="replace")
        diagnostic.feed(body)
        message = diagnostic.error_text[:250] or "no public error text"
        if "json" in error.headers.get("Content-Type", ""):
            detail = json.loads(body)
            message = str(detail.get("error", "")) + ": " + str(detail.get("error_description", ""))
        for value in [*values.values(), state, nonce, verifier]:
            message = message.replace(value, "[REDACTED]")
        cookie_handler = next(
            handler
            for handler in browser.handlers
            if isinstance(handler, urllib.request.HTTPCookieProcessor)
        )
        print(
            json.dumps(
                {
                    "login_cookie_metadata": [
                        {"name": cookie.name, "secure": cookie.secure, "path": cookie.path}
                        for cookie in cookie_handler.cookiejar
                    ],
                    "response_content_type": error.headers.get("Content-Type"),
                    "public_error": message[:300],
                }
            )
        )
        raise AssertionError(f"Keycloak login HTTP {error.code}: {message}") from None
    raise AssertionError("Keycloak did not issue a code")


def exchange(code, verifier):
    pair = "kryptroom-web-bff:" + values["KR_BFF_CLIENT_SECRET"]
    data = urllib.parse.urlencode(
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": CALLBACK,
            "code_verifier": verifier,
        }
    ).encode()
    request = urllib.request.Request(  # noqa: S310 — fixed loopback-only fixture URL
        ISSUER + "/protocol/openid-connect/token",
        data=data,
        headers={"Authorization": "Basic " + base64.b64encode(pair.encode()).decode()},
    )
    with urllib.request.urlopen(request, timeout=5) as response:  # noqa: S310
        return json.load(response)


code, verifier, nonce = authorization_code()
tokens = exchange(code, verifier)
validator = OIDCVerifier(
    OIDCConfiguration(ISSUER, "kryptroom-control-api", SecretStr(values["KR_API_CLIENT_SECRET"]))
)
identity = validator.verify_access_token(SecretStr(tokens["access_token"]))
require(bool(identity.subject), "Expected verified subject")
header = jwt.get_unverified_header(tokens["id_token"])
id_claims = jwt.decode(
    tokens["id_token"],
    validator._key(header["kid"]),
    algorithms=["RS256"],
    issuer=ISSUER,
    audience="kryptroom-web-bff",
)
require(id_claims["nonce"] == nonce, "ID token nonce failed")
try:
    exchange(code, verifier)
except urllib.error.HTTPError as error:
    require(error.code == 400, "Expected consumed code rejection")
else:
    raise AssertionError("Replayed authorization code accepted")
code, _, _ = authorization_code()
try:
    exchange(code, secrets.token_urlsafe(48))
except urllib.error.HTTPError as error:
    require(error.code == 400, "Expected wrong PKCE rejection")
else:
    raise AssertionError("Wrong PKCE accepted")
print(
    json.dumps(
        {
            "provider": "real Keycloak26.8.2",
            "authorization_code_pkce": "passed",
            "access_signature_claims_and_live_introspection": "passed",
            "id_token_nonce": "passed",
            "replayed_code": "rejected",
            "wrong_pkce": "rejected",
            "tokens_printed": False,
            "not_full_pr2_acceptance": True,
        }
    )
)
