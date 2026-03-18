"""views/duplist.py - duplicate file list with original/copy labelling"""

from __future__ import annotations

import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

import theme
from actions import delete_to_trash


def _fmt(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} TB"


def _date(path):
    try:
        return datetime.fromtimestamp(os.path.getmtime(path)).strftime(
            "%Y-%m-%d  %H:%M"
        )
    except OSError:
        return ""


class DupListView(ttk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)

        tb = ttk.Frame(self)
        tb.pack(fill="x", padx=theme.PAD_SMALL, pady=theme.PAD_SMALL)
        ttk.Button(tb, text="Delete selected (Recycle Bin)", command=self._del).pack(
            side="left"
        )
        ttk.Button(tb, text="Select all copies", command=self._sel_copies).pack(
            side="left", padx=theme.PAD_NORMAL
        )
        self._sv = tk.StringVar(value="Run a duplicate scan first.")
        ttk.Label(tb, textvariable=self._sv).pack(side="left", padx=theme.PAD_LARGE)

        cols = ("role", "name", "path", "size", "date", "group")
        self.tree = ttk.Treeview(
            self, columns=cols, show="headings", selectmode="extended"
        )

        self.tree.heading("role", text="Role")
        self.tree.heading("name", text="Filename")
        self.tree.heading("path", text="Full path")
        self.tree.heading("size", text="Size")
        self.tree.heading("date", text="Date modified")
        self.tree.heading("group", text="Group")

        self.tree.column("role", width=60, anchor="center", stretch=False)
        self.tree.column("name", width=180, stretch=False)
        self.tree.column("path", width=340, stretch=True)
        self.tree.column("size", width=80, anchor="e", stretch=False)
        self.tree.column("date", width=140, anchor="center", stretch=False)
        self.tree.column("group", width=55, anchor="center", stretch=False)

        self.tree.tag_configure("original", background=theme.COLOR_ORIGINAL_BG)
        self.tree.tag_configure("copy", background=theme.COLOR_COPY_BG)

        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def load(self, groups: list[list[str]]) -> None:
        self.tree.delete(*self.tree.get_children())
        waste = 0

        for gi, paths in enumerate(groups, 1):
            if not paths:
                continue
            try:
                ordered = sorted(paths, key=lambda p: os.path.getmtime(p))
            except OSError:
                ordered = paths[:]

            sz = os.path.getsize(ordered[0]) if os.path.exists(ordered[0]) else 0
            waste += sz * (len(ordered) - 1)

            for i, p in enumerate(ordered):
                role = "original" if i == 0 else "copy"
                self.tree.insert(
                    "",
                    "end",
                    tags=(role,),
                    values=(
                        role,
                        os.path.basename(p),
                        p,
                        _fmt(os.path.getsize(p)) if os.path.exists(p) else "?",
                        _date(p),
                        str(gi),
                    ),
                )

        total = sum(len(g) for g in groups)
        self._sv.set(
            f"{len(groups)} groups  *  {total} files total  *  "
            f"reclaimable: {_fmt(waste)}"
        )

    def _sel_copies(self):
        self.tree.selection_set(
            [
                iid
                for iid in self.tree.get_children()
                if "copy" in self.tree.item(iid, "tags")
            ]
        )

    def _del(self):
        sel = self.tree.selection()
        if not sel:
            return
        paths = [self.tree.item(s)["values"][2] for s in sel]
        if not messagebox.askyesno(
            "Confirm", f"Send {len(paths)} file(s) to Recycle Bin?"
        ):
            return
        errs = []
        for p in paths:
            success, msg = delete_to_trash(p)
            if not success:
                errs.append(f"{os.path.basename(p)}: {msg}")

        # Refresh tree - simpler to just delete selected items from view
        for iid in sel:
            self.tree.delete(iid)

        if errs:
            messagebox.showerror("Errors", "\n".join(errs))
