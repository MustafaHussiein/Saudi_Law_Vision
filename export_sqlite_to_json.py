"""
One-time export: legal_tech.db  ->  json_db/db.json
Run from the project root:   python export_sqlite_to_json.py
"""
import json
import os
import sqlite3

SRC = "legal_tech.db"
DST = os.path.join("json_db", "db.json")

con = sqlite3.connect(SRC)
con.row_factory = sqlite3.Row

tables = [
    r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
]

data = {}
for t in tables:
    data[t] = [dict(r) for r in con.execute(f'SELECT * FROM "{t}"')]
    print(f"{t:25s} {len(data[t])} rows")

os.makedirs("json_db", exist_ok=True)
with open(DST, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1, default=str)

print(f"\nSaved to {DST}")
