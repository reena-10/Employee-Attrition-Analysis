"""Run the full pipeline: python run_all.py"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = [
    "01_generate_data.py",    # skip this step if you use your own raw CSV
    "02_clean_data.py",
    "03_build_database.py",
    "04_run_sql_analysis.py",
    "05_eda_and_charts.py",
]

for step in STEPS:
    print(f"\n{'=' * 70}\n>> {step}\n{'=' * 70}")
    subprocess.run([sys.executable, str(ROOT / "src" / step)], check=True)
print("\nAll steps finished. See outputs/ for charts, SQL results and summaries.")
