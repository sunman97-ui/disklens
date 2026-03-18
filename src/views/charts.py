"""views/charts.py - bar charts via matplotlib embedded in tkinter"""
from __future__ import annotations
from tkinter import ttk
from collections import defaultdict
from pathlib import Path
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

P = ["#4A90D9","#5BA85A","#E67E22","#9B59B6","#E74C3C","#1ABC9C","#F39C12","#2980B9","#8E44AD","#27AE60"]

class BarChartView(ttk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)
        self.fig = Figure(figsize=(6,4), dpi=96, facecolor="#f5f5f5")
        self.ax  = self.fig.add_subplot(111)
        c = FigureCanvasTkAgg(self.fig, master=self)
        c.get_tk_widget().pack(fill="both", expand=True)
        self._c = c

    def load(self, children, top_n=15):
        top = sorted(children, key=lambda c: c["size"], reverse=True)[:top_n]
        labs = [c["label"][:28] for c in top]
        vals = [c["size"]/(1024**2) for c in top]
        self.ax.clear()
        self.ax.barh(labs[::-1], vals[::-1], color=P[:len(labs)], edgecolor="none")
        self.ax.set_xlabel("Size (MB)")
        self.ax.set_facecolor("#f5f5f5"); self.fig.patch.set_facecolor("#f5f5f5")
        self.ax.spines[["top","right"]].set_visible(False)
        self.fig.tight_layout(); self._c.draw()

class TypeChartView(ttk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)
        self.fig = Figure(figsize=(6,4), dpi=96, facecolor="#f5f5f5")
        self.ax  = self.fig.add_subplot(111)
        c = FigureCanvasTkAgg(self.fig, master=self)
        c.get_tk_widget().pack(fill="both", expand=True)
        self._c = c

    def load(self, file_list):
        by_ext = defaultdict(int)
        for f in file_list:
            ext = Path(f["path"]).suffix.lower() or "(none)"
            by_ext[ext] += f["size"]
        top = sorted(by_ext.items(), key=lambda x: x[1], reverse=True)[:12]
        labs = [e for e,_ in top]; vals = [s/(1024**2) for _,s in top]
        self.ax.clear()
        self.ax.barh(labs[::-1], vals[::-1], color=P[:len(labs)], edgecolor="none")
        self.ax.set_xlabel("Size (MB)")
        self.ax.set_facecolor("#f5f5f5"); self.fig.patch.set_facecolor("#f5f5f5")
        self.ax.spines[["top","right"]].set_visible(False)
        self.fig.tight_layout(); self._c.draw()
