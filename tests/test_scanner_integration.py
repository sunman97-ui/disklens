from __future__ import annotations

from pathlib import Path

from src.scanner import scan


def test_scan_integration(tmp_path: Path) -> None:
    """Verify that scan() correctly builds a tree from a real directory structure."""
    # Create a small directory tree
    # tmp_path/
    #   file1.txt (100 bytes)
    #   subdir/
    #     file2.txt (200 bytes)

    file1 = tmp_path / "file1.txt"
    file1.write_bytes(b"A" * 100)

    subdir = tmp_path / "subdir"
    subdir.mkdir()
    file2 = subdir / "file2.txt"
    file2.write_bytes(b"B" * 200)

    # Run the scan
    node = scan(str(tmp_path))

    # Verify the tree
    assert node.size == 300
    assert len(node.children) == 2  # file1.txt and subdir

    # Verify subdir contents
    subdir_node = next(c for c in node.children if c.is_dir)
    assert subdir_node.name == "subdir"
    assert subdir_node.size == 200
    assert len(subdir_node.children) == 1
    assert subdir_node.children[0].size == 200


def test_scan_safety_hard_stop() -> None:
    """Verify that scan() refuses to enter a blocked system path immediately."""
    # We don't need a real path here because the safety check happens at the start
    node = scan(r"C:\Windows")

    # It should return a node with 0 size and no children
    assert node.size == 0
    assert len(node.children) == 0
