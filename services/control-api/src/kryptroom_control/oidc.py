"""OIDC verification only; a valid identity conveys no organization authority."""

import base64
import json
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Literal, cast

import jwt
from pydantic import BaseModel, ConfigDict, Field, SecretStr, StrictInt, ValidationError


class AuthenticationFailed(Exception):
    def __init__(self) -> None:
        super().__init__("Authentication failed")


class IdentityProviderUnavailable(Exception):
    def __init__(self) -> None:
        super().__init__("Identity provider unavailable")


@dataclass(frozen=True)
class OIDCConfiguration:
    issuer: str
    introspection_client_id: str
    introspection_client_secret: SecretStr
    audience: str = "kryptroom-control-api"
    permitted_bff: str = "kryptroom-web-bff"
    local_http: bool = False
    transport_origin: str | None = None
    clock_skew: int = 30

    def __post_init__(self) -> None:
        parsed = urllib.parse.urlsplit(self.issuer)
        if (
            parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
            or not parsed.hostname
            or self.issuer.endswith("/")
            or not 0 <= self.clock_skew <= 60
            or len(self.introspection_client_secret.get_secret_value()) < 24
        ):
            raise ValueError("Invalid OIDC configuration")
        if parsed.scheme != "https" and not (
            self.local_http
            and parsed.scheme == "http"
            and parsed.hostname in ("localhost", "127.0.0.1", "::1")
        ):
            raise ValueError("OIDC requires HTTPS outside explicit loopback development")
        if self.transport_origin is not None:
            transport = urllib.parse.urlsplit(self.transport_origin)
            if (
                not self.local_http
                or parsed.hostname not in ("localhost", "127.0.0.1", "::1")
                or transport.scheme != "http"
                or transport.hostname != "keycloak"
                or transport.path not in ("", "/")
                or transport.username is not None
                or transport.password is not None
                or transport.query
                or transport.fragment
            ):
                raise ValueError("Invalid development-only OIDC transport mapping")


@dataclass(frozen=True)
class VerifiedIdentity:
    issuer: str
    subject: str
    display_name: str
    email_snapshot: str | None


class AccessClaims(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True, hide_input_in_errors=True)

    iss: str
    sub: str = Field(min_length=1, max_length=255)
    aud: str | list[str]
    exp: StrictInt = Field(gt=0)
    iat: StrictInt = Field(ge=0)
    nbf: StrictInt | None = None
    azp: str
    typ: Literal["Bearer"]
    name: str = Field(default="", max_length=120)
    preferred_username: str = Field(default="", max_length=120)
    email: str | None = Field(default=None, max_length=254)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        # An IdP redirect is not permission to send credentials to another origin.
        return None


class OIDCVerifier:
    """Bounded discovery/JWKS; strict signatures plus per-call introspection."""

    def __init__(self, configuration: OIDCConfiguration) -> None:
        self.configuration = configuration
        self._metadata: dict[str, Any] | None = None
        self._jwks: list[dict[str, Any]] = []
        self._keys_at = 0.0
        self._lock = threading.RLock()
        self._http = urllib.request.build_opener(NoRedirect())

    def _url(self, url: str) -> str:
        issuer = self.configuration.issuer
        # Discovery may only nominate endpoints belonging to this exact issuer.
        if not url.startswith(issuer + "/"):
            raise IdentityProviderUnavailable()
        if self.configuration.transport_origin:
            parsed = urllib.parse.urlsplit(url)
            return self.configuration.transport_origin.rstrip("/") + parsed.path
        return url

    def _json(self, url: str, token: SecretStr | None = None) -> dict[str, Any]:
        data = None
        headers = {"Accept": "application/json"}
        if token is not None:
            secret = self.configuration.introspection_client_secret.get_secret_value()
            pair = self.configuration.introspection_client_id + ":" + secret
            headers["Authorization"] = "Basic " + base64.b64encode(pair.encode()).decode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            data = urllib.parse.urlencode({"token": token.get_secret_value()}).encode()
        # _url accepts only the configured HTTPS issuer or explicit local mapping.
        request = urllib.request.Request(  # noqa: S310
            self._url(url), data=data, headers=headers
        )
        try:
            with self._http.open(request, timeout=2) as response:
                raw = response.read(1_048_577)
                if len(raw) > 1_048_576 or response.status != 200:
                    raise IdentityProviderUnavailable()
            result = json.loads(raw)
            if not isinstance(result, dict):
                raise IdentityProviderUnavailable()
            return cast(dict[str, Any], result)
        except (OSError, ValueError, urllib.error.URLError):
            raise IdentityProviderUnavailable() from None

    def _discovery(self) -> dict[str, Any]:
        with self._lock:
            if self._metadata is None:
                metadata = self._json(
                    self.configuration.issuer + "/.well-known/openid-configuration"
                )
                if metadata.get("issuer") != self.configuration.issuer:
                    raise IdentityProviderUnavailable()
                for name in ("jwks_uri", "introspection_endpoint"):
                    if not isinstance(metadata.get(name), str):
                        raise IdentityProviderUnavailable()
                    self._url(metadata[name])
                self._metadata = metadata
            return self._metadata

    def _key(self, kid: str) -> jwt.PyJWK:
        with self._lock:
            metadata = self._discovery()
            # Cached valid keys require no fetch. Unknown keys get one refresh.
            for refresh in (False, True):
                if refresh or time.monotonic() - self._keys_at >= 300 or not self._jwks:
                    response = self._json(metadata["jwks_uri"])
                    keys = response.get("keys")
                    if not isinstance(keys, list) or len(keys) > 100:
                        raise IdentityProviderUnavailable()
                    self._jwks = [key for key in keys if isinstance(key, dict)]
                    self._keys_at = time.monotonic()
                for key in self._jwks:
                    if (
                        key.get("kid") == kid
                        and key.get("kty") == "RSA"
                        and key.get("use", "sig") == "sig"
                        and key.get("alg", "RS256") == "RS256"
                        and "verify" in key.get("key_ops", ["verify"])
                    ):
                        try:
                            jwk = jwt.PyJWK.from_dict(key, algorithm="RS256")
                            if getattr(jwk.key, "key_size", 0) < 2048:
                                raise AuthenticationFailed()
                            return jwk
                        except (jwt.PyJWTError, ValueError, TypeError):
                            raise AuthenticationFailed() from None
            raise AuthenticationFailed()

    def verify_access_token(self, token: SecretStr) -> VerifiedIdentity:
        raw = token.get_secret_value()
        if not 1 <= len(raw) <= 16384:
            raise AuthenticationFailed()
        try:
            header = jwt.get_unverified_header(raw)
            kid = header.get("kid")
            if (
                header.get("alg") != "RS256"
                or header.get("crit")
                or not isinstance(kid, str)
                or not 1 <= len(kid) <= 128
            ):
                raise AuthenticationFailed()
            payload = jwt.decode(
                raw,
                self._key(kid),
                algorithms=["RS256"],
                issuer=self.configuration.issuer,
                audience=self.configuration.audience,
                leeway=self.configuration.clock_skew,
                options={"require": ["iss", "sub", "aud", "exp", "iat", "azp", "typ"]},
            )
            claims = AccessClaims.model_validate(payload)
            if claims.azp != self.configuration.permitted_bff or claims.exp <= claims.iat:
                raise AuthenticationFailed()
        except (jwt.PyJWTError, ValidationError, ValueError, TypeError):
            raise AuthenticationFailed() from None
        active = self._json(self._discovery()["introspection_endpoint"], token)
        if (
            active.get("active") is not True
            or active.get("sub") != claims.sub
            or active.get("client_id") != self.configuration.permitted_bff
        ):
            raise AuthenticationFailed()
        return VerifiedIdentity(
            issuer=claims.iss,
            subject=claims.sub,
            display_name=claims.name or claims.preferred_username,
            email_snapshot=claims.email,
        )
