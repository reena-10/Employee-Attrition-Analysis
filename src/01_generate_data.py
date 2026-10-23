"""
Step 1 - Generate a synthetic HR dataset (IBM "HR Analytics" style).

Why synthetic?  So the project runs end-to-end with zero downloads.  The column
names match the public IBM HR Analytics Employee Attrition dataset, so you can
drop the real CSV in as data/raw/employee_attrition_raw.csv and every later
step still works (see README).

The generator also injects realistic "dirt" (missing values, duplicates,
inconsistent labels, impossible ages) so the cleaning step has real work to do.
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N = 1500
TARGET_RATE = 0.16  # overall attrition rate we calibrate to

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "employee_attrition_raw.csv"

rng = np.random.default_rng(SEED)

# ----------------------------------------------------------------- structure
DEPT_ROLES = {
    "Sales": ["Sales Executive", "Sales Representative", "Sales Manager"],
    "Research & Development": ["Research Scientist", "Laboratory Technician", "Research Director"],
    "Human Resources": ["HR Executive", "HR Manager"],
    "Finance": ["Financial Analyst", "Accountant", "Finance Manager"],
    "IT": ["Software Engineer", "Systems Analyst", "IT Manager"],
}
DEPTS = list(DEPT_ROLES)
DEPT_P = [0.28, 0.40, 0.07, 0.10, 0.15]
DEPT_INCOME_BUMP = {"Sales": 0, "Research & Development": 0, "Human Resources": -300,
                    "Finance": 600, "IT": 900}
DEPT_RISK = {"Sales": 0.35, "Research & Development": -0.15, "Human Resources": 0.15,
             "Finance": -0.10, "IT": 0.0}

# ------------------------------------------------------------------ demographics
age = np.clip(rng.normal(37, 9, N).round(), 18, 60).astype(int)
gender = rng.choice(["Male", "Female"], N, p=[0.58, 0.42])
marital = rng.choice(["Single", "Married", "Divorced"], N, p=[0.32, 0.46, 0.22])
distance = rng.integers(1, 30, N)

# ------------------------------------------------------------------ career
total_years = np.clip(((age - 21).clip(min=0)) * rng.uniform(0.35, 1.0, N), 0, 40).round().astype(int)
years_company = np.minimum(total_years, rng.gamma(2.2, 3.0, N).round().astype(int))
years_promo = np.minimum(years_company, rng.poisson(1.8, N))
years_mgr = np.minimum(years_company, rng.poisson(3.0, N))
num_companies = np.clip(rng.poisson(2.0, N), 0, 9)

level = (1 + (total_years > 5) + (total_years > 12) + (total_years > 20) + (total_years > 28)
         + rng.integers(-1, 2, N))
level = np.clip(level, 1, 5).astype(int)

dept = rng.choice(DEPTS, N, p=DEPT_P)
role = np.array([
    DEPT_ROLES[d][-1] if lv >= 4 else rng.choice(DEPT_ROLES[d][:-1])
    for d, lv in zip(dept, level)
])

income = (2200 + level * 2800 + total_years * 90
          + np.array([DEPT_INCOME_BUMP[d] for d in dept])
          + rng.normal(0, 700, N))
income = (np.clip(income, 1500, None) / 10).round().astype(int) * 10

# ------------------------------------------------------------------ work conditions
overtime = rng.choice(["Yes", "No"], N, p=[0.28, 0.72])
travel = rng.choice(["Non-Travel", "Travel_Rarely", "Travel_Frequently"], N, p=[0.10, 0.70, 0.20])
job_sat = rng.choice([1, 2, 3, 4], N, p=[0.19, 0.19, 0.31, 0.31])
wlb = rng.choice([1, 2, 3, 4], N, p=[0.05, 0.23, 0.61, 0.11])
env_sat = rng.choice([1, 2, 3, 4], N, p=[0.19, 0.19, 0.31, 0.31])
hike = rng.integers(11, 26, N)
training = rng.integers(0, 7, N)
stock = rng.choice([0, 1, 2, 3], N, p=[0.43, 0.40, 0.11, 0.06])

# ------------------------------------------------------------------ attrition model
z_income = (income - income.mean()) / income.std()
base = (
    1.15 * (overtime == "Yes")
    + 0.55 * (travel == "Travel_Frequently") - 0.50 * (travel == "Non-Travel")
    - 0.035 * (age - 37)
    - 0.55 * z_income
    + 0.90 * (years_company <= 2)
    + 0.35 * (3 - job_sat)
    + 0.35 * (3 - wlb)
    + 0.03 * distance
    + 0.12 * years_promo
    + 0.45 * (stock == 0)
    + 0.30 * (marital == "Single")
    + 0.10 * num_companies
    + np.array([DEPT_RISK[d] for d in dept])
)

sigmoid = lambda x: 1 / (1 + np.exp(-x))
lo, hi = -10.0, 5.0
for _ in range(60):  # bisection: find intercept that hits the target rate
    mid = (lo + hi) / 2
    if sigmoid(base + mid).mean() > TARGET_RATE:
        hi = mid
    else:
        lo = mid
attrition = np.where(rng.random(N) < sigmoid(base + mid), "Yes", "No")

df = pd.DataFrame({
    "EmployeeNumber": np.arange(1001, 1001 + N),
    "Age": age, "Gender": gender, "MaritalStatus": marital,
    "Department": dept, "JobRole": role, "JobLevel": level,
    "MonthlyIncome": income, "PercentSalaryHike": hike, "StockOptionLevel": stock,
    "TrainingTimesLastYear": training,
    "TotalWorkingYears": total_years, "YearsAtCompany": years_company,
    "YearsSinceLastPromotion": years_promo, "YearsWithCurrManager": years_mgr,
    "NumCompaniesWorked": num_companies, "DistanceFromHome": distance,
    "BusinessTravel": travel, "OverTime": overtime,
    "JobSatisfaction": job_sat, "WorkLifeBalance": wlb, "EnvironmentSatisfaction": env_sat,
    "Attrition": attrition,
})

# ------------------------------------------------------------------ inject "dirt"
raw = df.copy()
raw.loc[rng.choice(N, 28, replace=False), "MonthlyIncome"] = np.nan          # missing income
raw.loc[rng.choice(N, 18, replace=False), "DistanceFromHome"] = np.nan       # missing distance
raw.loc[rng.choice(N, 3, replace=False), "Age"] = 150                        # impossible ages

messy = rng.choice(N, 45, replace=False)                                     # label inconsistencies
raw.loc[messy[:15], "Department"] = raw.loc[messy[:15], "Department"].str.upper()
raw.loc[messy[15:30], "Department"] = " " + raw.loc[messy[15:30], "Department"].str.lower() + " "
raw.loc[messy[30:38], "Attrition"] = raw.loc[messy[30:38], "Attrition"].str.lower()
raw.loc[messy[38:], "Attrition"] = raw.loc[messy[38:], "Attrition"] + " "

raw = pd.concat([raw, raw.sample(12, random_state=SEED)], ignore_index=True)  # exact duplicates
raw = raw.sample(frac=1, random_state=SEED).reset_index(drop=True)            # shuffle

raw["MonthlyIncome"] = raw["MonthlyIncome"].astype("Int64")
raw.to_csv(OUT, index=False)
print(f"Saved {len(raw):,} raw rows x {raw.shape[1]} columns -> {OUT.relative_to(ROOT)}")
print(f"True attrition rate before cleaning noise: {(df['Attrition'] == 'Yes').mean():.1%}")
