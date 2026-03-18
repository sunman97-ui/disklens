# largelist.py
from __future__ import annotations

import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Any

import theme
from actions import delete_to_trash


def _fmt(n: float) -> str:
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} TB"


def _date(path):
    try:
        t = os.path.getmtime(path)
        return datetime.fromtimestamp(t).strftime("%Y-%m-%d  %H:%M")
    except OSError:
        return ""


class LargeListView(ttk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)
        self._checks: dict[str, tk.BooleanVar] = {}

        tb = ttk.Frame(self)
        tb.pack(fill="x", padx=theme.PAD_NORMAL, pady=theme.PAD_NORMAL)
        ttk.Button(tb, text="Select all", command=self._sel_all).pack(side="left")
        ttk.Button(tb, text="Select none", command=self._sel_none).pack(
            side="left", padx=theme.PAD_SMALL
        )
        ttk.Separator(tb, orient="vertical").pack(
            side="left", fill="y", padx=theme.PAD_NORMAL
        )
        ttk.Button(tb, text="Delete selected (Recycle Bin)", command=self._delete).pack(
            side="left"
        )
        self._sv = tk.StringVar(value="Run a scan first.")
        ttk.Label(tb, textvariable=self._sv).pack(side="right", padx=theme.PAD_NORMAL)

        outer = ttk.Frame(self)
        outer.pack(fill="both", expand=True)
        self._canvas = tk.Canvas(outer, highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._inner = ttk.Frame(self._canvas)
        self._win_id = self._canvas.create_window(
            (0, 0), window=self._inner, anchor="nw"
        )
        self._inner.bind("<Configure>", self._on_inner_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind(
            "<MouseWheel>",
            lambda e: self._canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )

    def _on_inner_configure(self, _e=None):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, e):
        self._canvas.itemconfig(self._win_id, width=e.width)

    def load(self, file_list: list[dict[str, Any]], top_n: int = 20) -> None:
        for w in self._inner.winfo_children():
            w.destroy()
        self._checks.clear()

        top = sorted(file_list, key=lambda f: f["size"], reverse=True)[:top_n]

        # header
        hdr = ttk.Frame(self._inner)
        hdr.pack(fill="x", padx=theme.PAD_NORMAL, pady=(theme.PAD_SMALL, 0))
        ttk.Label(hdr, text="", width=3).pack(side="left")
        ttk.Label(hdr, text="File", font=theme.FONT_BOLD, anchor="w").pack(
            side="left", fill="x", expand=True
        )
        ttk.Label(
            hdr, text="Date modified", font=theme.FONT_BOLD, width=16, anchor="center"
        ).pack(side="right", padx=(0, theme.PAD_SMALL))
        ttk.Label(hdr, text="Size", font=theme.FONT_BOLD, width=10, anchor="e").pack(
            side="right", padx=(0, theme.PAD_NORMAL)
        )
        ttk.Separator(self._inner, orient="horizontal").pack(
            fill="x", padx=theme.PAD_NORMAL, pady=2
        )

        for i, f in enumerate(top):
            row = ttk.Frame(self._inner)
            row.pack(fill="x", padx=theme.PAD_NORMAL, pady=1)

            var = tk.BooleanVar(value=False)
            self._checks[f["path"]] = var

            ttk.Checkbutton(row, variable=var).pack(side="left")
            ttk.Label(
                row,
                text=f"#{i + 1}",
                width=3,
                foreground=theme.COLOR_GRAY,
                font=theme.FONT_HINT,
            ).pack(side="left")

            fname = os.path.basename(f["path"])
            lbl = ttk.Label(row, text=fname, anchor="w", cursor="hand2")
            lbl.pack(side="left", fill="x", expand=True)
            lbl.bind("<Button-1>", lambda e, v=var: v.set(not v.get()))  # type: ignore[misc]

            tip = f["path"]
            lbl.bind("<Enter>", lambda e, t=tip: self._sv.set(t))  # type: ignore[misc]
            lbl.bind("<Leave>", lambda e: self._sv.set(self._status_text()))

            ttk.Label(
                row,
                text=_date(f["path"]),
                width=16,
                anchor="center",
                foreground=theme.COLOR_TEXT_DIM,
            ).pack(side="right", padx=(0, theme.PAD_SMALL))
            ttk.Label(
                row, text=_fmt(f["size"]), width=10, anchor="e", foreground="#555"
            ).pack(side="right")

        self._sv.set(self._status_text())

    def _status_text(self) -> str:
        checked = sum(1 for v in self._checks.values() if v.get())
        total = len(self._checks)
        if checked:
            sz = sum(
                os.path.getsize(p)
                for p, v in self._checks.items()
                if v.get() and os.path.exists(p)
            )
            return f"{checked} of {total} selected  ({_fmt(sz)} selected)"
        return f"Showing top {total} largest files"

    def _sel_all(self):
        for v in self._checks.values():
            v.set(True)
        self._sv.set(self._status_text())

    def _sel_none(self):
        for v in self._checks.values():
            v.set(False)
        self._sv.set(self._status_text())

    def _delete(self):
        paths = [p for p, v in self._checks.items() if v.get()]
        if not paths:
            return
        total_size = sum(os.path.getsize(p) for p in paths if os.path.exists(p))
        if not messagebox.askyesno(
            "Confirm delete",
            f"Send {len(paths)} file(s) ({_fmt(total_size)}) to the Recycle Bin?",
        ):
            return
        errs = []
        for p in paths:
            success, msg = delete_to_trash(p)
            if success:
                del self._checks[p]
            else:
                errs.append(f"{os.path.basename(p)}: {msg}")
        self._rebuild_rows()
        if errs:
            messagebox.showerror("Some files could not be deleted", "\n".join(errs))

    def _rebuild_rows(self):
        self._checks = {p: v for p, v in self._checks.items() if os.path.exists(p)}
        self._sv.set(self._status_text())
