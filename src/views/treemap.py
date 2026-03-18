"""views/treemap.py - squarified treemap with drill-down"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import squarify

COLORS = ["#4A90D9","#5BA85A","#E67E22","#9B59B6","#E74C3C","#1ABC9C","#F39C12","#2980B9"]

def _fmt(n):
    for u in ("B","KB","MB","GB"):
        if n < 1024: return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} TB"

class TreemapView(ttk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)
        self._crumbs = []
        bar = ttk.Frame(self); bar.pack(fill="x", padx=4, pady=(4,0))
        ttk.Button(bar, text="^ Up", width=6, command=self._up).pack(side="left")
        self._cv = tk.StringVar(value="")
        ttk.Label(bar, textvariable=self._cv).pack(side="left", padx=8)
        self.canvas = tk.Canvas(self, bg="#1e1e2e", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _: self._draw())
        self.canvas.bind("<Button-1>", self._click)
        self._cur = []

    def load(self, children):
        self._crumbs.clear()
        self._cur = [c for c in children if c["size"] > 0]
        self._cv.set("/"); self._draw()

    def _draw(self):
        c = self.canvas; c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 2 or h < 2 or not self._cur: return
        sizes = [i["size"] for i in self._cur]
        if not sum(sizes): return
        rects = squarify.squarify(squarify.normalize_sizes(sizes, w-2, h-2), x=1, y=1, dx=w-2, dy=h-2)
        for i, (item, r) in enumerate(zip(self._cur, rects)):
            x0, y0, pw, ph = r["x"], r["y"], r["dx"], r["dy"]
            tag = f"c{i}"
            c.create_rectangle(x0, y0, x0+pw, y0+ph, fill=COLORS[i%len(COLORS)], outline="#1e1e2e", width=2, tags=tag)
            if pw > 40 and ph > 20:
                c.create_text(x0+pw/2, y0+ph/2-8, text=item["label"], fill="white",
                    font=("Segoe UI", max(8, min(13, int(pw/10)))), width=pw-8, tags=tag)
                c.create_text(x0+pw/2, y0+ph/2+10, text=_fmt(item["size"]), fill="#cccccc",
                    font=("Segoe UI", max(7, min(10, int(pw/14)))), tags=tag)

    def _click(self, e):
        for iid in reversed(self.canvas.find_overlapping(e.x, e.y, e.x, e.y)):
            for tag in self.canvas.gettags(iid):
                if tag.startswith("c") and tag[1:].isdigit():
                    node = self._cur[int(tag[1:])]
                    if node.get("children"):
                        self._crumbs.append((self._cv.get(), self._cur))
                        self._cur = [c for c in node["children"] if c["size"] > 0]
                        self._cv.set(self._cv.get().rstrip("/") + "/" + node["label"])
                        self._draw()
                    return

    def _up(self):
        if self._crumbs:
            label, prev = self._crumbs.pop()
            self._cur = prev; self._cv.set(label); self._draw()
