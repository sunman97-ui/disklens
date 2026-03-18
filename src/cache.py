"""cache.py - SQLite cache for scan results"""
from __future__ import annotations
import json, sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "scan_cache.db"

def _connect():
    con = sqlite3.connect(DB_PATH)
    con.execute("""CREATE TABLE IF NOT EXISTS scans (
        root TEXT PRIMARY KEY, scanned_at TEXT NOT NULL, data TEXT NOT NULL)""")
    con.commit(); return con

def save(root, data):
    from datetime import datetime
    con = _connect()
    con.execute("INSERT OR REPLACE INTO scans VALUES (?, ?, ?)",
                (root, datetime.now().isoformat(), json.dumps(data)))
    con.commit(); con.close()

def load(root):
    con = _connect()
    row = con.execute("SELECT data, scanned_at FROM scans WHERE root = ?", (root,)).fetchone()
    con.close()
    return {"data": json.loads(row[0]), "scanned_at": row[1]} if row else None

def clear(root):
    con = _connect()
    con.execute("DELETE FROM scans WHERE root = ?", (root,))
    con.commit(); con.close()
