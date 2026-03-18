from __future__ import annotations

from src.scanner import _is_blocked_name, _is_blocked_path


def test_blocked_names() -> None:
    """Verify system-critical names are blocked."""
    assert _is_blocked_name("Windows") is True
    assert _is_blocked_name("System32") is True
    assert _is_blocked_name("$Recycle.Bin") is True
    assert _is_blocked_name("Documents") is False
    assert _is_blocked_name("my_folder") is False


def test_blocked_paths() -> None:
    """Verify system-critical path segments are blocked."""
    assert _is_blocked_path(r"C:\Windows\System32") is True
    assert _is_blocked_path(r"D:\SomeData\$Recycle.Bin\Files") is True
    assert _is_blocked_path(r"C:\Users\User\Downloads\report.pdf") is False


def test_safe_roots_logic() -> None:
    """Verify path safety logic from main.py (simulated here)."""
    from main import _is_under_safe_root

    safe_roots = [r"C:\Users\John\Downloads", r"C:\software"]

    assert _is_under_safe_root(r"C:\Users\John\Downloads\test.txt", safe_roots) is True
    assert _is_under_safe_root(r"C:\software\disklens", safe_roots) is True
    assert _is_under_safe_root(r"C:\Windows", safe_roots) is False
    assert _is_under_safe_root(r"C:\Users\John\Documents", safe_roots) is False
