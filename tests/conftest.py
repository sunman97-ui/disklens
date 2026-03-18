from __future__ import annotations

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_send2trash(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Fixture to mock send2trash.send2trash to prevent actual file deletions."""
    mock = MagicMock()
    monkeypatch.setattr("send2trash.send2trash", mock)
    return mock
