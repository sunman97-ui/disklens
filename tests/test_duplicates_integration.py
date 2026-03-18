from __future__ import annotations

from pathlib import Path

from src.duplicates import find_duplicates


def test_find_duplicates_integration(tmp_path: Path) -> None:
    """Verify that find_duplicates identifies real file groups in a directory."""
    # Create a structure with duplicates
    # tmp_path/
    #   report.pdf
    #   report (1).pdf  <- Duplicate
    #   other.txt       <- Not a duplicate
    
    (tmp_path / "report.pdf").write_text("content")
    (tmp_path / "report (1).pdf").write_text("content")
    (tmp_path / "other.txt").write_text("content")
    
    groups = find_duplicates(str(tmp_path))
    
    assert len(groups) == 1
    assert len(groups[0]) == 2
    
    filenames = [Path(p).name for p in groups[0]]
    assert "report.pdf" in filenames
    assert "report (1).pdf" in filenames

def test_find_duplicates_empty_dir(tmp_path: Path) -> None:
    """Verify find_duplicates returns empty list for directory with no duplicates."""
    (tmp_path / "file1.txt").write_text("a")
    (tmp_path / "file2.txt").write_text("b")
    
    groups = find_duplicates(str(tmp_path))
    assert len(groups) == 0
