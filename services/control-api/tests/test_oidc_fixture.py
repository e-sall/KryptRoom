import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "render_realm",
    Path(__file__).resolve().parents[1] / "scripts/keycloak/render_realm.py",
)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def test_fixture_resolves_only_explicitly_supplied_secret():
    assert module.render_realm({"secret": "${KR_TEST_SECRET}"}, {"KR_TEST_SECRET": "a" * 32}) == {
        "secret": "a" * 32
    }


@pytest.mark.parametrize("value", ["${HOME}", "${KR_UNDECLARED}", "prefix${KR_TEST_SECRET}"])
def test_arbitrary_environment_expansion_refused(value):
    with pytest.raises(ValueError):
        module.render_realm({"secret": value}, {"KR_TEST_SECRET": "a" * 32})
