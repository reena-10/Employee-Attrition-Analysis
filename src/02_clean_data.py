"""
Step 2 - Clean the raw data with Pandas / NumPy and log every change.

Checks: duplicates, inconsistent labels, impossible values, missing values,
logical consistency, outliers (flagged only).  Output: a tidy CSV used by all
later steps plus outputs/cleaning_log.txt.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "employee_attrition_raw.csv"
CLEAN = ROOT / "data" / "processed" / "employee_attrition_clean.csv"
LOG = ROOT / "outputs" / "cleaning_log.txt"

log_lines = []


def log(msg):
    print(msg)
    log_lines.append(msg)


df = pd.read_csv(RAW)
log(f"Raw shape: {df.shape[0]:,} rows x {df.shape[1]} columns")

# 1. Missing values overview ---------------------------------------------------
missing = df.isna().sum()
missing = missing[missing > 0]
log("\n[1] Missing values before cleaning:")
log(missing.to_string() if len(missing) else "    none")

# 2. Duplicates ----------------------------------------------------------------
before = len(df)
df = df.drop_duplicates().drop_duplicates(subset="EmployeeNumber", keep="first")
log(f"\n[2] Removed {before - len(df)} duplicate rows")

# 3. Text labels: trim whitespace, unify casing --------------------------------
text_cols = df.select_dtypes(include=["object", "string"]).columns
for col in text_cols:
    df[col] = df[col].astype("string").str.strip()

canonical_dept = {"sales": "Sales", "research & development": "Research & Development",
                  "human resources": "Human Resources", "finance": "Finance", "it": "IT"}
dept_before = df["Department"].nunique()
df["Department"] = df["Department"].str.lower().map(canonical_dept).fillna(df["Department"])
df["Attrition"] = df["Attrition"].str.capitalize()
log(f"\n[3] Standardised text labels. Department variants: {dept_before} -> {df['Department'].nunique()}; "
    f"Attrition values: {sorted(df['Attrition'].dropna().unique())}")

# 4. Impossible values -> treat as missing, then impute ------------------------
bad_age = ~df["Age"].between(18, 65)
log(f"\n[4] Impossible ages (outside 18-65) set to missing: {int(bad_age.sum())}")
df.loc[bad_age, "Age"] = np.nan

# 5. Impute missing values -----------------------------------------------------
n_inc = int(df["MonthlyIncome"].isna().sum())
df["MonthlyIncome"] = df["MonthlyIncome"].astype("float")
df["MonthlyIncome"] = df["MonthlyIncome"].fillna(df.groupby("JobLevel")["MonthlyIncome"].transform("median"))
n_dist = int(df["DistanceFromHome"].isna().sum())
df["DistanceFromHome"] = df["DistanceFromHome"].fillna(df["DistanceFromHome"].median())
n_age = int(df["Age"].isna().sum())
df["Age"] = df["Age"].fillna(df.groupby("JobLevel")["Age"].transform("median"))
log(f"\n[5] Imputed MonthlyIncome ({n_inc}, median by JobLevel), "
    f"DistanceFromHome ({n_dist}, overall median), Age ({n_age}, median by JobLevel)")

# 6. Logical consistency -------------------------------------------------------
bad_tenure = df["YearsAtCompany"] > df["TotalWorkingYears"]
df.loc[bad_tenure, "TotalWorkingYears"] = df.loc[bad_tenure, "YearsAtCompany"]
log(f"\n[6] Fixed rows where YearsAtCompany > TotalWorkingYears: {int(bad_tenure.sum())}")

# 7. Outliers (report only) ----------------------------------------------------
q1, q3 = df["MonthlyIncome"].quantile([0.25, 0.75])
upper = q3 + 1.5 * (q3 - q1)
n_out = int((df["MonthlyIncome"] > upper).sum())
log(f"\n[7] MonthlyIncome outliers above IQR fence ({upper:,.0f}): {n_out} "
    f"- kept, they are plausible senior salaries")

# 8. Types + target flag -------------------------------------------------------
int_cols = ["Age", "MonthlyIncome", "DistanceFromHome", "TotalWorkingYears", "YearsAtCompany"]
df[int_cols] = df[int_cols].round().astype(int)
df["AttritionFlag"] = (df["Attrition"] == "Yes").astype(int)
df = df.sort_values("EmployeeNumber").reset_index(drop=True)

assert df.isna().sum().sum() == 0, "NaNs remain after cleaning"
assert set(df["Attrition"].unique()) <= {"Yes", "No"}

log(f"\nClean shape: {df.shape[0]:,} rows x {df.shape[1]} columns | "
    f"overall attrition rate: {df['AttritionFlag'].mean():.1%}")

df.to_csv(CLEAN, index=False)
LOG.write_text("\n".join(log_lines), encoding="utf-8")
print(f"\nSaved -> {CLEAN.relative_to(ROOT)}")
