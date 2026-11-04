"""Static publication-scope checks; never dispatch a workflow."""

import fnmatch
import importlib.util
from pathlib import Path

import yaml

SERVICE = Path(__file__).resolve().parents[1]
REPO = SERVICE.parent.parent


def workflow(name: str) -> dict:
    config = yaml.safe_load((REPO / ".github/workflows" / name).read_text())
    # PyYAML's YAML 1.1 loader reads the GitHub YAML 1.2 key "on" as boolean True.
    if True in config:
        config["on"] = config.pop(True)
    return config


def matches_paths(config: dict, event: str, paths: list[str]) -> bool:
    trigger = config["on"].get(event)
    if trigger is None:
        return event in config["on"]
    patterns = trigger.get("paths")
    return patterns is None or any(
        fnmatch.fnmatchcase(p, pattern) for p in paths for pattern in patterns
    )


def test_new_ci_is_scoped_readonly_and_has_no_crypto_command() -> None:
    config = workflow("control-api-foundation.yml")
    assert config["permissions"] == {"contents": "read"}
    assert config["on"]["pull_request"]["branches"] == ["dev"]
    assert "workflow_dispatch" in config["on"]
    assert matches_paths(
        config, "pull_request", ["services/control-api/src/kryptroom_control/app.py"]
    )
    assert not matches_paths(config, "pull_request", ["apps/web/src/app/page.tsx"])
    assert not matches_paths(config, "pull_request", ["engines/zk/example.rs"])
    commands = "\n".join(
        step.get("run", "") for step in config["jobs"]["m9-control-foundation"]["steps"]
    )
    assert "pip_audit" in commands and "--require-hashes" in commands
    assert "compose-acceptance.py" in commands
    assert not any(
        word in commands.lower() for word in ("groth16", "sp1", "cast send", "forge script")
    )
    for step in config["jobs"]["m9-control-foundation"]["steps"]:
        if "uses" in step:
            assert len(step["uses"].split("@")[1]) == 40


def test_existing_proof_and_chain_routes_are_not_silently_exempted() -> None:
    proof = workflow("state-proof-acceptance.yml")
    m9_paths = [
        "services/control-api/pyproject.toml",
        "docs/m9/pr1/IMPLEMENTATION-REPORT.md",
        ".github/workflows/control-api-foundation.yml",
        "CHANGELOG.md",
        "TODO.md",
        "docs/DECISIONS.md",
    ]
    assert not matches_paths(proof, "pull_request", m9_paths)
    assert matches_paths(proof, "pull_request", m9_paths + ["engines/zk/changed.rs"])
    assert matches_paths(proof, "pull_request", ["tests/state_proof/generate_fixture.py"])
    assert set(workflow("public-chain-anchor-live.yml")["on"]) == {"workflow_dispatch"}
    spec = importlib.util.spec_from_file_location(
        "m9_ci_scope_review", REPO / ".github/ci_scope.py"
    )
    assert spec is not None and spec.loader is not None
    scope = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scope)
    # M9 is conservatively core under the current baseline: publication needs review.
    assert scope.requires_core(m9_paths, lambda _: None, lambda _: None)


def test_local_compose_is_isolated_and_pinned() -> None:
    compose = yaml.safe_load((SERVICE / "compose.yml").read_text())
    services = compose["services"]
    assert set(services) == {"postgres", "api", "migrate", "tests"}
    assert "@sha256:" in services["postgres"]["image"]
    assert "ports" not in services["postgres"]
    assert services["api"]["ports"] == ["127.0.0.1:8001:8000"]
    assert services["api"]["secrets"] == ["app_password"]
    assert services["migrate"]["secrets"] == ["migrator_password"]
    assert compose["networks"]["database"]["internal"] is True
    assert services["api"]["networks"] == ["database", "ingress"]
    assert services["postgres"]["networks"] == ["database"]
    assert services["api"]["read_only"] is True
    assert services["api"]["cap_drop"] == ["ALL"]
    dockerfile = (SERVICE / "Dockerfile").read_text()
    assert "python:3.12.16-slim-bookworm@sha256:" in dockerfile
    assert "USER 10001:10001" in dockerfile
    assert "--no-access-log" in dockerfile and "--no-proxy-headers" in dockerfile
