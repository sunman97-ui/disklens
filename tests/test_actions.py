from __future__ import annotations

import os
from unittest.mock import MagicMock

import pytest

from src.actions import delete_to_trash


def test_delete_to_trash_success(
    monkeypatch: pytest.MonkeyPatch, mock_send2trash: MagicMock
) -> None:
    """Verify success path for delete_to_trash."""
    monkeypatch.setattr("os.path.exists", lambda _: True)

    success, msg = delete_to_trash(r"C:\test\file.txt")

    assert success is True
    assert "Recycle Bin" in msg
    mock_send2trash.assert_called_once_with(os.path.normpath(r"C:\test\file.txt"))


def test_delete_to_trash_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify failure path when file does not exist."""
    monkeypatch.setattr("os.path.exists", lambda _: False)

    success, msg = delete_to_trash(r"C:\missing.txt")

    assert success is False
    assert "File not found" in msg


def test_delete_to_trash_exception(
    monkeypatch: pytest.MonkeyPatch, mock_send2trash: MagicMock
) -> None:
    """Verify error handling when send2trash raises an exception."""
    monkeypatch.setattr("os.path.exists", lambda _: True)
    mock_send2trash.side_effect = Exception("Permisson denied")

    success, msg = delete_to_trash(r"C:\restricted.txt")

    assert success is False
    assert "Permisson denied" in msg
