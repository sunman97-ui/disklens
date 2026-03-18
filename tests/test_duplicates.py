from __future__ import annotations

import pytest

from src.duplicates import _normalise


@pytest.mark.parametrize(
    "input_name, expected",
    [
        ("report.pdf", "report.pdf"),
        ("report (1).pdf", "report.pdf"),
        ("report(1).pdf", "report.pdf"),
        ("report - Copy.pdf", "report.pdf"),
        ("report - copy.pdf", "report.pdf"),
        ("report - Copy (2).pdf", "report.pdf"),
        ("REPORT.PDF", "report.pdf"),
        ("report(2).pdf", "report.pdf"),
        ("normal_file.txt", "normal_file.txt"),
        ("  report  .pdf", "report.pdf"),
    ],
)
def test_normalise_filename(input_name: str, expected: str) -> None:
    """Ensure filenames are correctly normalised by stripping Windows copy suffixes."""
    assert _normalise(input_name) == expected
