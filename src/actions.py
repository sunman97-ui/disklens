"""actions.py - Centralised file system operations."""

from __future__ import annotations

import os

import send2trash


def delete_to_trash(path: str) -> tuple[bool, str]:
    """
    Safely move a file or folder to the system Recycle Bin.
    Returns (success, message).
    """
    # Normalise to Windows backslash path to avoid send2trash issues
    p = os.path.normpath(path)

    if not os.path.exists(p):
        return False, f"File not found: {p}"

    try:
        send2trash.send2trash(p)
        return True, "Moved to Recycle Bin"
    except Exception as e:
        return False, str(e)
