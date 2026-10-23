"""
Step 3 - Load the cleaned CSV into a normalised SQLite database
(departments, employees, compensation) using sql/01_schema.sql.
"""
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "processed" / "employee_attrition_clean.csv"
DB = ROOT / "data" / "processed" / "attrition.db"
SCHEMA = ROOT / "sql" / "01_schema.sql"

df = pd.read_csv(CLEAN)

departments = (pd.DataFrame({"dept_name": sorted(df["Department"].unique())})
               .reset_index(names="dept_id"))
departments["dept_id"] += 1
dept_map = dict(zip(departments["dept_name"], departments["dept_id"]))

employees = pd.DataFrame({
    "emp_id": df["EmployeeNumber"], "age": df["Age"], "gender": df["Gender"],
    "marital_status": df["MaritalStatus"], "dept_id": df["Department"].map(dept_map),
    "job_role": df["JobRole"], "job_level": df["JobLevel"],
    "total_working_years": df["TotalWorkingYears"], "years_at_company": df["YearsAtCompany"],
    "years_since_last_promotion": df["YearsSinceLastPromotion"],
    "years_with_curr_manager": df["YearsWithCurrManager"],
    "num_companies_worked": df["NumCompaniesWorked"], "distance_from_home": df["DistanceFromHome"],
    "business_travel": df["BusinessTravel"], "overtime": df["OverTime"],
    "job_satisfaction": df["JobSatisfaction"], "work_life_balance": df["WorkLifeBalance"],
    "environment_satisfaction": df["EnvironmentSatisfaction"], "attrition": df["Attrition"],
})

compensation = pd.DataFrame({
    "emp_id": df["EmployeeNumber"], "monthly_income": df["MonthlyIncome"],
    "percent_salary_hike": df["PercentSalaryHike"], "stock_option_level": df["StockOptionLevel"],
    "training_times_last_year": df["TrainingTimesLastYear"],
})

with sqlite3.connect(DB) as conn:
    conn.executescript(SCHEMA.read_text())
    departments.to_sql("departments", conn, if_exists="append", index=False)
    employees.to_sql("employees", conn, if_exists="append", index=False)
    compensation.to_sql("compensation", conn, if_exists="append", index=False)
    for t in ("departments", "employees", "compensation"):
        n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t:<14} {n:>6,} rows")

print(f"Saved -> {DB.relative_to(ROOT)}")
