r"""scanner.py - fast recursive directory scanner with Windows safety guards.

Safety rules applied before entering any directory or reading any file:
  - Blocked root paths: Windows, System32, SysWOW64, WinSxS, boot, Recovery,
    pagefile.sys, hiberfil.sys, swapfile.sys, $Recycle.Bin, System Volume
    Information, EFI, ProgramData\Microsoft, and others.
  - Reparse points (junctions, symlinks) are never followed.
  - Any path containing a blocked segment anywhere in it is skipped.
  - PermissionError and OSError are silently skipped.
  - Files are never opened -- only stat() is called.
"""

from __future__ import annotations

import os
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from os import DirEntry
from pathlib import Path

# ---------------------------------------------------------------------------
# Safety blocklist
# ---------------------------------------------------------------------------

# Exact directory names (case-insensitive) that should never be entered.
_BLOCKED_NAMES: frozenset[str] = frozenset(
    {
        # Core Windows OS
        "windows",
        "system32",
        "syswow64",
        "sysnative",
        "winsxs",
        "servicing",
        "panther",
        # Boot / recovery
        "boot",
        "recovery",
        "efi",
        "$recycle.bin",
        "recycler",
        "system volume information",
        # Driver stores
        "driverstore",
        "drivers",
        # Virtual memory / hibernate (files, but block as names too)
        "pagefile.sys",
        "hiberfil.sys",
        "swapfile.sys",
        # MS telemetry / update internals
        "softwaredistribution",
        "catroot",
        "catroot2",
        # ProgramData sub-paths that are risky
        "microsoft",  # only blocks under ProgramData -- see path-segment check
        # Virtualisation
        "wsl",
        "lxss",
    }
)

# If any of these strings appear anywhere in the normalised path, skip it.
# Use lowercase path segments.
_BLOCKED_PATH_SEGMENTS: tuple[str, ...] = (
    r"\windows" + os.sep,
    r"\windows\\",
    r"/windows/",
    "system32",
    "syswow64",
    "winsxs",
    "$recycle.bin",
    "system volume information",
    "pagefile.sys",
    "hiberfil.sys",
    "swapfile.sys",
    r"\boot" + os.sep,
    r"/boot/",
)

# Files at the root of a drive that should never be touched.
_BLOCKED_ROOT_FILES: frozenset[str] = frozenset(
    {
        "pagefile.sys",
        "hiberfil.sys",
        "swapfile.sys",
        "bootmgr",
        "bootnxt",
        "ntldr",
        "io.sys",
        "msdos.sys",
        "config.sys",
        "autoexec.bat",
    }
)


def _is_blocked_name(name: str) -> bool:
    return name.lower() in _BLOCKED_NAMES


def _is_blocked_path(path: str) -> bool:
    low = path.lower()
    return any(seg in low for seg in _BLOCKED_PATH_SEGMENTS)


def _is_safe_entry(entry: DirEntry[str], root: str) -> bool:
    """Return True if this entry is safe to include / descend into."""
    try:
        # Never follow reparse points (symlinks, junctions, mount points)
        if entry.is_symlink():
            return False
        # Check name blocklist
        if _is_blocked_name(entry.name):
            return False
        # Check full path for blocked segments
        return not _is_blocked_path(entry.path)
    except OSError:
        return False


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class FileNode:
    path: str
    size: int
    is_dir: bool
    children: list[FileNode] = field(default_factory=list)

    @property
    def name(self) -> str:
        return os.path.basename(self.path) or self.path


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------


def scan(
    root: str,
    progress_cb: Callable[[str], None] | None = None,
    cancel_event: threading.Event | None = None,
) -> FileNode:
    """
    Scan *root* and return a FileNode tree.
    Never opens files -- only calls stat().
    Skips all blocked/system paths and reparse points.
    """
    root = str(Path(root).resolve())

    # Hard stop if someone points at a blocked root
    if _is_blocked_name(os.path.basename(root)) or _is_blocked_path(root):
        node = FileNode(path=root, size=0, is_dir=True)
        return node

    def _scan_dir(path: str) -> FileNode:
        if cancel_event and cancel_event.is_set():
            return FileNode(path=path, size=0, is_dir=True)

        node = FileNode(path=path, size=0, is_dir=True)
        if progress_cb:
            progress_cb(path)

        try:
            with os.scandir(path) as it:
                entries = list(it)
        except (PermissionError, OSError):
            return node

        subdirs: list[str] = []
        for e in entries:
            if not _is_safe_entry(e, root):
                continue
            try:
                if e.is_dir(follow_symlinks=False):
                    subdirs.append(e.path)
                else:
                    sz = e.stat().st_size
                    # Skip root-level system files by name
                    if (
                        os.path.dirname(e.path) == root
                        and e.name.lower() in _BLOCKED_ROOT_FILES
                    ):
                        continue
                    child = FileNode(path=e.path, size=sz, is_dir=False)
                    node.children.append(child)
                    node.size += sz
            except OSError:
                continue

        for dpath in subdirs:
            child = _scan_dir(dpath)
            node.children.append(child)
            node.size += child.size

        return node

    # Scan top-level subdirs in parallel
    top = FileNode(path=root, size=0, is_dir=True)
    if progress_cb:
        progress_cb(root)

    try:
        with os.scandir(root) as it:
            top_entries = list(it)
    except (PermissionError, OSError):
        return top

    top_dirs: list[str] = []
    for e in top_entries:
        if not _is_safe_entry(e, root):
            continue
        try:
            if e.is_dir(follow_symlinks=False):
                top_dirs.append(e.path)
            else:
                sz = e.stat().st_size
                if e.name.lower() in _BLOCKED_ROOT_FILES:
                    continue
                child = FileNode(path=e.path, size=sz, is_dir=False)
                top.children.append(child)
                top.size += sz
        except OSError:
            continue

    with ThreadPoolExecutor(max_workers=min(8, len(top_dirs) or 1)) as pool:
        futures = {pool.submit(_scan_dir, d): d for d in top_dirs}
        for fut in as_completed(futures):
            try:
                child = fut.result()
                top.children.append(child)
                top.size += child.size
            except Exception:
                continue

    return top
