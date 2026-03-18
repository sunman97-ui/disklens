"""main.py - DiskLens.  Run: python main.py"""
from __future__ import annotations
import os, sys, threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

sys.path.insert(0, "src")
from scanner import scan
from duplicates import find_duplicates
from views.treemap import TreemapView
from views.charts import BarChartView, TypeChartView
from views.duplist import DupListView
from views.largelist import LargeListView


def _fmt(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024: return f"{n:.1f} {u}"
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
        os.path.join(home, "software")
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
    def __init__(self):
        super().__init__()
        self.title("DiskLens"); self.geometry("1100x700"); self.minsize(800, 500)
        self._path = None
        self._data = None
        self._safe_roots = _safe_roots()
        self._build()

    def _build(self):
        # --- toolbar ---
        bar = ttk.Frame(self, padding=(8, 6)); bar.pack(fill="x")
        self._pv = tk.StringVar(value="No folder selected")
        ttk.Label(bar, textvariable=self._pv, width=52).pack(side="left")
        ttk.Button(bar, text="Browse...",       command=self._browse).pack(side="left", padx=4)
        ttk.Button(bar, text="Scan",            command=self._scan).pack(side="left")
        ttk.Button(bar, text="Find duplicates", command=self._dups).pack(side="left", padx=8)
        self._sv = tk.StringVar(value="Ready.")
        ttk.Label(bar, textvariable=self._sv, foreground="gray").pack(side="right", padx=8)

        # --- safe roots hint bar ---
        hint = ttk.Frame(self, padding=(8, 0)); hint.pack(fill="x")
        roots_str = "  |  ".join(os.path.basename(r) for r in self._safe_roots)
        ttk.Label(
            hint,
            text=f"Safe scan folders: {roots_str}",
            foreground="gray",
            font=("Segoe UI", 8),
        ).pack(side="left")

        # --- notebook ---
        nb = ttk.Notebook(self); nb.pack(fill="both", expand=True, padx=8, pady=(4, 8))
        self._tm = TreemapView(nb);   self._bc = BarChartView(nb)
        self._tc = TypeChartView(nb); self._dl = DupListView(nb)
        self._ll = LargeListView(nb)
        nb.add(self._tm, text="  Treemap  ")
        nb.add(self._bc, text="  Top folders  ")
        nb.add(self._tc, text="  File types  ")
        nb.add(self._dl, text="  Duplicates  ")
        nb.add(self._ll, text="  Largest files  ")

    def _browse(self):
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
                "This protects your system files from being accidentally modified."
            )
            return

        self._path = d
        self._pv.set(d)

    def _validate(self) -> bool:
        if not self._path:
            messagebox.showinfo("DiskLens", "Please select a folder first.")
            return False
        if not _is_under_safe_root(self._path, self._safe_roots):
            messagebox.showerror("Folder not allowed",
                                 "The selected path is outside the safe scan area.")
            return False
        return True

    def _scan(self):
        if not self._validate(): return
        self._sv.set("Scanning..."); self.update_idletasks()

        def run():
            node = scan(
                self._path,
                progress_cb=lambda p: self._sv.set(f"  {p[-70:]}"),
            )

            def td(n):
                return {
                    "label": n.name, "size": n.size, "path": n.path,
                    "children": [td(c) for c in n.children if c.is_dir],
                }

            def af(n):
                if not n.is_dir: yield {"path": n.path, "size": n.size}
                for c in n.children: yield from af(c)

            self._data = {"root": td(node), "files": list(af(node))}
            self.after(0, self._done)

        threading.Thread(target=run, daemon=True).start()

    def _done(self):
        ch = self._data["root"]["children"]
        self._tm.load(ch)
        self._bc.load(ch)
        self._tc.load(self._data["files"])
        self._ll.load(self._data["files"])
        total = self._data["root"]["size"]
        count = len(self._data["files"])
        self._sv.set(f"Done - {_fmt(total)} across {count} files")

    def _dups(self):
        if not self._validate(): return
        self._sv.set("Finding duplicates..."); self.update_idletasks()

        def run():
            groups = find_duplicates(
                self._path,
                progress_cb=lambda p: self._sv.set(f"  checking {p[-60:]}"),
            )
            self.after(0, lambda: self._dl.load(groups))
            self.after(0, lambda: self._sv.set(
                f"Done - {len(groups)} duplicate groups found"))

        threading.Thread(target=run, daemon=True).start()


if __name__ == "__main__":
    App().mainloop()