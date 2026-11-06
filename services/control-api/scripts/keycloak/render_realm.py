"""Resolve only declared fixture placeholders; never enable IdP system-variable expansion."""

import re


def render_realm(value: object, secrets: dict[str, str]) -> object:
    if isinstance(value, dict):
        return {key: render_realm(item, secrets) for key, item in value.items()}
    if isinstance(value, list):
        return [render_realm(item, secrets) for item in value]
    if isinstance(value, str) and "${" in value:
        match = re.fullmatch(r"\$\{(KR_[A-Z_]+)\}", value)
        if match is None or match[1] not in secrets:
            raise ValueError("Unresolved or undeclared fixture placeholder")
        secret = secrets[match[1]]
        if re.fullmatch(r"[A-Za-z0-9_-]{24,128}", secret) is None:
            raise ValueError("Invalid fixture credential")
        return secret
    return value
