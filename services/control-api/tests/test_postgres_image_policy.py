"""Never let the acceptance controller silently test a moving image tag."""

import runpy
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.mark.parametrize("image", ["postgres:17", "postgres:latest", "sha256:bad", "--privileged"])
def test_moving_or_invalid_image_refused_before_docker(image):
    script = Path(__file__).resolve().parents[1] / "scripts/postgres-image-acceptance.py"
    with (
        patch("sys.argv", [str(script), "--image=" + image]),
        patch("subprocess.run") as process,
        pytest.raises(ValueError, match="immutable"),
    ):
        runpy.run_path(str(script), run_name="__main__")
    process.assert_not_called()
