"""duplicates.py - find duplicates by normalised filename within the same folder.

Rules:
  - Files must be in the same parent directory.
  - Files must have the same normalised name (stem stripped of Windows copy
    suffixes, extension lowercased).

This means:
  downloads/report.pdf  +  downloads/report (1).pdf   -> duplicates  (same dir)
  downloads/report.pdf  +  downloads/sub/report.pdf   -> NOT duplicates (different dir)
  project/__init__.py   +  project/api/__init__.py    -> NOT duplicates (different dir)
"""
from __future__ import annotations
import os
import re
from collections import defaultdict
from typing import Callable, Optional


_COPY_RE = re.compile(
    r"""
    \s*
    (?:
        -\s*[Cc]opy
        (?:\s*\(\d+\))?
        |
        \(\d+\)
    )
    $
    """,
    re.VERBOSE,
)


def _normalise(filename: str) -> str:
    stem, ext = os.path.splitext(filename)
    stem = _COPY_RE.sub("", stem).strip()
    return (stem + ext).lower()


def find_duplicates(
    root: str,
    progress_cb: Optional[Callable[[str], None]] = None,
) -> list[list[str]]:
    """
    Return groups of duplicate files.
    Each group contains >= 2 files that share the same parent directory
    and the same normalised filename.
    """
    # key: (parent_dir, normalised_name)  ->  [full_paths]
    buckets: dict[tuple[str, str], list[str]] = defaultdict(list)

    for dirpath, _dirs, filenames in os.walk(root):
        for fname in filenames:
            if progress_cb:
                progress_cb(os.path.join(dirpath, fname))
            key = _normalise(fname)
            if not key:
                continue
            buckets[(dirpath, key)].append(os.path.join(dirpath, fname))

    return [paths for paths in buckets.values() if len(paths) > 1]