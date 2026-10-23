"""
Step 4 - Run every query in sql/02_analysis_queries.sql against the SQLite
database, print the results and save each one as a CSV.
"""
import re
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "processed" / "attrition.db"
QUERIES = ROOT / "sql" / "02_analysis_queries.sql"
OUT = ROOT / "outputs" / "sql_results"

parts = re.split(r"^-- name:\s*(\w+)\s*$", QUERIES.read_text(), flags=re.M)
queries = dict(zip(parts[1::2], parts[2::2]))

pd.set_option("display.width", 140)
with sqlite3.connect(DB) as conn:
    for name, sql in queries.items():
        result = pd.read_sql_query(sql, conn)
        result.to_csv(OUT / f"{name}.csv", index=False)
        print(f"\n=== {name} ===")
        print(result.to_string(index=False))

print(f"\n{len(queries)} queries executed -> {OUT.relative_to(ROOT)}/")
