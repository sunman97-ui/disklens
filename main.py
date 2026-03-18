"""main.py - DiskLens.  Run: python main.py"""

from __future__ import annotations

import os
import sys
import threading
import tkinter as tk
from collections.abc import Generator
from tkinter import filedialog, messagebox, ttk
from typing import Any

sys.path.insert(0, "src")
import theme
from duplicates import find_duplicates
from scanner import scan
from views.charts import BarChartView, TypeChartView
from views.duplist import DupListView
from views.largelist import LargeListView
from views.treemap import TreemapView


def _fmt(n: float) -> str:
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} TB"


# ---------------------------------------------------------------------------
# Safe-root enforcement
# ---------------------------------------------------------------------------


def _safe_roots() -> list[str]:
    """Return normalised absolute paths of user folders that are safe to scan."""
    home = os.path.expanduser("~")
    candidates = [
        os.path.join(home, "Downloads"),
        os.path.join(home, "Documents"),
        os.path.join(home, "Desktop"),
        os.path.join(home, "Pictures"),
        os.path.join(home, "Videos"),
        os.path.join(home, "Music"),
        os.path.join(home, "OneDrive"),
        os.path.join(home, "Dropbox"),
        os.path.join(home, "Google Drive"),
        os.path.join(home, "software"),
    ]
    # Only include folders that actually exist on this machine
    return [os.path.normpath(p) for p in candidates if os.path.isdir(p)]


def _is_under_safe_root(path: str, safe_roots: list[str]) -> bool:
    p = os.path.normpath(path).lower()
    for root in safe_roots:
        r = root.lower()
        if p == r or p.startswith(r + os.sep):
            return True
    return False


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("DiskLens")
        self.geometry("1100x700")
        self.minsize(800, 500)

        # Load icon relative to this file
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
        if os.path.exists(icon_path):
            self.iconphoto(False, tk.PhotoImage(file=icon_path))

        self._path: str | None = None
        self._data: dict[str, Any] | None = None
        self._safe_roots = _safe_roots()
        self._build()

    def _build(self) -> None:
        # --- toolbar ---
        bar = ttk.Frame(self, padding=theme.TOOLBAR_PADDING)
        bar.pack(fill="x")
        self._pv = tk.StringVar(value="No folder selected")
        ttk.Label(bar, textvariable=self._pv, width=52).pack(side="left")
        ttk.Button(bar, text="Browse...", command=self._browse).pack(
            side="left", padx=theme.PAD_SMALL
        )
        ttk.Button(bar, text="Scan", command=self._scan).pack(side="left")
        ttk.Button(bar, text="Find duplicates", command=self._dups).pack(
            side="left", padx=theme.PAD_NORMAL
        )
        self._sv = tk.StringVar(value="Ready.")
        ttk.Label(bar, textvariable=self._sv, foreground=theme.COLOR_GRAY).pack(
            side="right", padx=theme.PAD_NORMAL
        )

        # --- safe roots hint bar ---
        hint = ttk.Frame(self, padding=theme.HINT_BAR_PADDING)
        hint.pack(fill="x")
        roots_str = "  |  ".join(os.path.basename(r) for r in self._safe_roots)
        ttk.Label(
            hint,
            text=f"Safe scan folders: {roots_str}",
            foreground=theme.COLOR_GRAY,
            font=theme.FONT_HINT,
        ).pack(side="left")

        # --- notebook ---
        nb = ttk.Notebook(self)
        nb.pack(
            fill="both",
            expand=True,
            padx=theme.PAD_NORMAL,
            pady=theme.NOTEBOOK_PADDING[1],
        )
        self._tm = TreemapView(nb)  # type: ignore[no-untyped-call]
        self._bc = BarChartView(nb)  # type: ignore[no-untyped-call]
        self._tc = TypeChartView(nb)  # type: ignore[no-untyped-call]
        self._dl = DupListView(nb)  # type: ignore[no-untyped-call]
        self._ll = LargeListView(nb)  # type: ignore[no-untyped-call]
        nb.add(self._tm, text="  Treemap  ")
        nb.add(self._bc, text="  Top folders  ")
        nb.add(self._tc, text="  File types  ")
        nb.add(self._dl, text="  Duplicates  ")
        nb.add(self._ll, text="  Largest files  ")

    def _browse(self) -> None:
        # Open the file dialog starting inside the first safe root
        start = self._safe_roots[0] if self._safe_roots else os.path.expanduser("~")
        d = filedialog.askdirectory(title="Select folder to analyse", initialdir=start)
        if not d:
            return

        d = os.path.normpath(d)

        if not _is_under_safe_root(d, self._safe_roots):
            safe_list = "\n".join(f"  - {r}" for r in self._safe_roots)
            messagebox.showerror(
                "Folder not allowed",
                f"'{d}' is outside the safe scan area.\n\n"
                f"DiskLens only scans within:\n{safe_list}\n\n"
                "This protects your system files from being accidentally modified.",
            )
            return

        self._path = d
        self._pv.set(d)

    def _validate(self) -> bool:
        if not self._path:
            messagebox.showinfo("DiskLens", "Please select a folder first.")
            return False
        if not _is_under_safe_root(self._path, self._safe_roots):
            messagebox.showerror(
                "Folder not allowed", "The selected path is outside the safe scan area."
            )
            return False
        return True

    def _scan(self) -> None:
        if not self._validate():
            return
        self._sv.set("Scanning...")
        self.update_idletasks()

        def run() -> None:
            assert self._path is not None
            def progress_cb(p: str) -> None:
                self._sv.set(f"  {p[-70:]}")
            node = scan(
                self._path,
                progress_cb=progress_cb,
            )

            def td(n: Any) -> dict[str, Any]:
                return {
                    "label": n.name,
                    "size": n.size,
                    "path": n.path,
                    "children": [td(c) for c in n.children if c.is_dir],
                }

            def af(n: Any) -> Generator[dict[str, Any], None, None]:
                if not n.is_dir:
                    yield {"path": n.path, "size": n.size}
                for c in n.children:
                    yield from af(c)

            self._data = {"root": td(node), "files": list(af(node))}
            self.after(0, self._done)

        threading.Thread(target=run, daemon=True).start()

    def _done(self) -> None:
        assert self._data is not None
        ch = self._data["root"]["children"]
        self._tm.load(ch)  # type: ignore[no-untyped-call]
        self._bc.load(ch)  # type: ignore[no-untyped-call]
        self._tc.load(self._data["files"])  
        self._ll.load(self._data["files"])
        total = float(self._data["root"]["size"])
        count = len(self._data["files"])
        self._sv.set(f"Done - {_fmt(total)} across {count} files")

    def _dups(self) -> None:
        if not self._validate():
            return
        self._sv.set("Finding duplicates...")
        self.update_idletasks()

        def run() -> None:
            assert self._path is not None
            def progress_cb(p: str) -> None:
                self._sv.set(f"  checking {p[-60:]}")
            groups = find_duplicates(
                self._path,
                progress_cb=progress_cb,
            )
            def load_done() -> None:
                self._dl.load(groups)
            self.after(0, load_done)
            def set_done() -> None:
                self._sv.set(f"Done - {len(groups)} duplicate groups found")
            self.after(0, set_done)

        threading.Thread(target=run, daemon=True).start()


if __name__ == "__main__":
    App().mainloop()
