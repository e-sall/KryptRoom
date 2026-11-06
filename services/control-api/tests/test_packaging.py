import tarfile
from pathlib import Path

from hatchling.builders.sdist import SdistBuilder


def test_source_distribution_excludes_private_runtime_even_without_gitignore(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    manifest = Path(__file__).resolve().parents[1] / "pyproject.toml"
    (project / "pyproject.toml").write_bytes(manifest.read_bytes())
    source = project / "src/kryptroom_control/__init__.py"
    source.parent.mkdir(parents=True)
    source.write_text('"""Synthetic package for build-boundary regression."""')
    sentinel = b"DO-NOT-PACK-LOCAL-SECRET"
    for name in [
        ".runtime/secrets/app_password",
        ".venv/credential.txt",
        "src/kryptroom_control/__pycache__/cached.pyc",
        "src/stale.egg-info/PKG-INFO",
    ]:
        path = project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(sentinel)
    output = tmp_path / "dist"
    output.mkdir()
    archive = next(SdistBuilder(str(project)).build(directory=str(output)))
    with tarfile.open(archive) as bundle:
        names = bundle.getnames()
        assert any(name.endswith("src/kryptroom_control/__init__.py") for name in names)
        for member in bundle.getmembers():
            assert not any(
                part in member.name for part in (".runtime", ".venv", "__pycache__", ".egg-info")
            )
            stream = bundle.extractfile(member) if member.isfile() else None
            if stream is not None:
                assert sentinel not in stream.read()
