"""Explicit PR2 delivery controls; no workflow, provider, proof or chain dispatch."""

import hashlib
import json
from pathlib import Path

import yaml

SERVICE = Path(__file__).resolve().parents[1]
REPO = SERVICE.parent.parent


def test_identity_ci_is_additive_strict_and_does_not_reuse_an_exception():
    path = REPO / ".github/workflows/control-api-identity.yml"
    source = path.read_text()
    config = yaml.safe_load(source)
    trigger = config.get("on", config.get(True))
    assert "workflow_dispatch" in trigger
    assert "paths" not in trigger["pull_request"]
    assert config["permissions"] == {"contents": "read"}
    assert set(config["jobs"]) == {"m9-identity-organizations"}
    assert "npm audit --json --audit-level=moderate" in source
    assert "continue-on-error" not in source
    assert "persist-credentials: false" in source
    assert "--require-hashes" in source
    assert "identity-stack-acceptance.py --disposable" in source
    assert "Explicit identity non-applicability" in source
    for prohibited in ("groth16", "cast send", "forge script", "M8-SEC-001", "M8-SEC-002"):
        assert prohibited not in source


def test_browser_does_not_receive_daemon_sql_operator_or_server_token_keys():
    source = (SERVICE / "scripts/identity-acceptance.py").read_text()
    # Only inspect the browser process command, not the separate trusted controller.
    command = source.split("process = subprocess.Popen(", 1)[1].split("phases =", 1)[0]
    assert "/var/run/docker.sock" not in command
    assert "/usr/bin/docker" not in command
    assert "--privileged" not in command
    assert '"10001:10001"' in command
    assert '"no-new-privileges:true"' in command
    assert '"--read-only"' in command
    assert "target=/run/test-users,readonly" in command
    for name in ("operator_password", "bff_password", "bff_encryption_key", "oidc_bff_secret"):
        assert name not in command


def test_identity_fixture_remains_loopback_only_and_exactly_pinned():
    source = (SERVICE / "compose.identity.yml").read_text()
    assert "listen_addresses=127.0.0.1" in source
    assert "KC_HTTP_HOST: 127.0.0.1" in source
    assert "KC_HTTP_ENABLED: 'false'" in source
    assert "KC_HOSTNAME: https://127.0.0.1:8444" in source
    assert "--host, 127.0.0.1" in source
    assert "CONTROL_OIDC_CLIENT_SECRET_FILE" in source
    dockerfile = (REPO / "apps/web/Dockerfile.identity").read_text()
    assert "HOSTNAME=127.0.0.1 PORT=3004" in dockerfile
    assert "playwright:v1.64.1-noble@sha256:" in dockerfile
    assert "node:22.23.4-bookworm-slim@sha256:" in dockerfile
    assert "USER 10001:10001" in dockerfile


def test_pr1_upgrade_preserves_original_bootstrap_and_migration_reference():
    fixture = SERVICE / "tests/fixtures/pr1-init-db.sh"
    provenance = json.loads((fixture.parent / "pr1-baseline.json").read_text())
    assert provenance["commit"] == "d8a5c0aa7ed845c31bd2ff40c1b3491246c6cf83"
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == provenance["init_db_sha256"]
    assert (
        hashlib.sha256(
            (SERVICE / "migrations/versions/0001_foundation.py").read_bytes()
        ).hexdigest()
        == provenance["migration_0001_sha256"]
    )
