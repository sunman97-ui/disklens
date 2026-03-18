from __future__ import annotations

from pathlib import Path

import tomllib

import src


def test_version_consistency() -> None:
    """Verify that the version in pyproject.toml matches src/__init__.py."""
    root_dir = Path(__file__).parent.parent
    pyproject_path = root_dir / "pyproject.toml"

    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)

    toml_version = pyproject_data["project"]["version"]
    code_version = src.__version__

    assert toml_version == code_version
