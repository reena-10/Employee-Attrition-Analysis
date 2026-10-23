"""
Step 5 - Exploratory data analysis (Pandas / NumPy) and charts (Matplotlib / Seaborn).

Outputs
  outputs/eda_summary.txt    - dataset overview + attrition tables
  outputs/key_findings.txt   - headline numbers used in the README
  outputs/charts/*.png       - all figures
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "processed" / "employee_attrition_clean.csv"
CHARTS = ROOT / "outputs" / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", context="notebook")
RED, BLUE, GREY = "#d1495b", "#3d6f9e", "#8a8a8a"

df = pd.read_csv(CLEAN)
overall = df["AttritionFlag"].mean() * 100

# --------------------------------------------------------------------------- feature engineering
df["AgeGroup"] = pd.cut(df["Age"], [17, 24, 34, 44, 54, 100], labels=["18-24", "25-34", "35-44", "45-54", "55+"])
df["SalaryBand"] = pd.cut(df["MonthlyIncome"], [0, 4999, 6999, 8999, 11999, np.inf],
                          labels=["<5k", "5-7k", "7-9k", "9-12k", "12k+"])
df["ExperienceBand"] = pd.cut(df["TotalWorkingYears"], [-1, 2, 5, 10, 20, 100],
                              labels=["0-2 yrs", "3-5 yrs", "6-10 yrs", "11-20 yrs", "20+ yrs"])
df["TenureBand"] = pd.cut(df["YearsAtCompany"], [-1, 1, 3, 6, 10, 100],
                          labels=["0-1 yrs", "2-3 yrs", "4-6 yrs", "7-10 yrs", "10+ yrs"])
df["Travel"] = pd.Categorical(df["BusinessTravel"], ["Non-Travel", "Travel_Rarely", "Travel_Frequently"], ordered=True)
df["RiskFlags"] = ((df["OverTime"] == "Yes").astype(int) + (df["JobSatisfaction"] <= 2).astype(int)
                   + (df["MonthlyIncome"] < 5000).astype(int) + (df["YearsAtCompany"] <= 2).astype(int))

# --------------------------------------------------------------------------- 1. EDA summary
lines = []
lines.append(f"Rows: {len(df):,} | Columns: {df.shape[1]}")
lines.append(f"Overall attrition rate: {overall:.1f}% ({df['AttritionFlag'].sum()} leavers)\n")
lines.append("Numeric summary:\n" + df[["Age", "MonthlyIncome", "TotalWorkingYears", "YearsAtCompany",
                                          "DistanceFromHome"]].describe().round(1).to_string())
for col in ["Department", "AgeGroup", "SalaryBand", "ExperienceBand", "TenureBand", "OverTime", "Travel",
            "MaritalStatus", "StockOptionLevel", "JobSatisfaction", "WorkLifeBalance"]:
    t = (df.groupby(col, observed=True)["AttritionFlag"].agg(headcount="count", leavers="sum", rate="mean"))
    t["rate"] = (t["rate"] * 100).round(1)
    lines.append(f"\nAttrition by {col}:\n{t.to_string()}")
(ROOT / "outputs" / "eda_summary.txt").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines[:12]))


# --------------------------------------------------------------------------- 2. chart helpers
def rate_table(data, col):
    t = data.groupby(col, observed=True)["AttritionFlag"].agg(rate="mean", leavers="sum", n="count").reset_index()
    t["rate"] *= 100
    t[col] = t[col].astype(str)
    return t


def plot_rate(ax, col, title, xlabel, data=df):
    """Bar chart of attrition rate per group; red = above company average."""
    t = rate_table(data, col)
    palette = {g: (RED if r > overall else BLUE) for g, r in zip(t[col], t["rate"])}
    sns.barplot(data=t, x=col, y="rate", hue=col, palette=palette, legend=False, order=list(t[col]), ax=ax)
    for i, r in enumerate(t["rate"]):
        ax.text(i, r + t["rate"].max() * 0.02, f"{r:.1f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.axhline(overall, ls="--", lw=1.2, color=GREY, label=f"Company average {overall:.1f}%")
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 1.0), frameon=False, fontsize=9)
    ax.set_xticks(range(len(t)))
    ax.set_xticklabels([f"{g}\n(n={n})" for g, n in zip(t[col], t["n"])], fontsize=9)
    ax.set_ylim(0, t["rate"].max() * 1.22)
    ax.set_title(title, fontsize=12, fontweight="bold", loc="left")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Attrition rate (%)")


def save(fig, name):
    fig.tight_layout()
    fig.savefig(CHARTS / name, dpi=150, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------- 3. charts
# 01 overall split
fig, ax = plt.subplots(figsize=(5.5, 5.5))
counts = df["Attrition"].value_counts().reindex(["No", "Yes"])
ax.pie(counts, labels=[f"Stayed\n{counts['No']:,}", f"Left\n{counts['Yes']:,}"], colors=[BLUE, RED],
       startangle=90, counterclock=False, wedgeprops=dict(width=0.42, edgecolor="white"),
       textprops=dict(fontsize=11))
ax.text(0, 0, f"{overall:.1f}%\nattrition", ha="center", va="center", fontsize=15, fontweight="bold")
ax.set_title("Overall attrition", fontsize=12, fontweight="bold")
save(fig, "01_overall_attrition.png")

for fname, col, title, xlabel in [
    ("02_attrition_by_department.png", "Department", "Attrition rate by department", "Department"),
    ("03_attrition_by_age_group.png", "AgeGroup", "Attrition rate by age group", "Age group"),
    ("04_attrition_by_salary_band.png", "SalaryBand", "Attrition rate by monthly salary band", "Monthly income"),
    ("05_attrition_by_experience.png", "ExperienceBand", "Attrition rate by total work experience",
     "Total working years"),
    ("06_attrition_by_tenure.png", "TenureBand", "Attrition rate by years at the company", "Years at company"),
    ("11_attrition_by_risk_flags.png", "RiskFlags", "Attrition rate by number of risk flags",
     "Risk flags (overtime, low satisfaction, income < 5k, tenure <= 2 yrs)"),
]:
    fig, ax = plt.subplots(figsize=(8.5, 5))
    plot_rate(ax, col, title, xlabel)
    if col == "Department":
        ax.tick_params(axis="x", labelsize=8)
    save(fig, fname)

# 07 overtime + travel
fig, axes = plt.subplots(1, 2, figsize=(11, 5))
plot_rate(axes[0], "OverTime", "Overtime", "Works overtime?")
plot_rate(axes[1], "Travel", "Business travel", "Travel frequency")
axes[1].set_ylabel("")
fig.suptitle("Work conditions vs attrition", fontsize=14, fontweight="bold", y=1.02)
save(fig, "07_overtime_and_travel.png")

# 08 leavers vs stayers
fig, axes = plt.subplots(1, 3, figsize=(12, 4.8))
for ax, (col, label) in zip(axes, [("MonthlyIncome", "Monthly income"), ("Age", "Age"),
                                   ("YearsAtCompany", "Years at company")]):
    sns.boxplot(data=df, x="Attrition", y=col, hue="Attrition", order=["No", "Yes"],
                palette={"No": BLUE, "Yes": RED}, legend=False, width=0.55, ax=ax)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Stayed", "Left"])
    ax.set_xlabel("")
    ax.set_ylabel(label)
    med = df.groupby("Attrition")[col].median()
    ax.set_title(f"{label}\nmedian: stayed {med['No']:,.0f} vs left {med['Yes']:,.0f}", fontsize=11)
fig.suptitle("Profile of leavers vs stayers", fontsize=14, fontweight="bold", y=1.03)
save(fig, "08_leavers_vs_stayers.png")

# 09 heatmap overtime x job satisfaction
pivot = (df.pivot_table(values="AttritionFlag", index="OverTime", columns="JobSatisfaction", aggfunc="mean") * 100)
fig, ax = plt.subplots(figsize=(7, 3.6))
sns.heatmap(pivot, annot=True, fmt=".1f", cmap="Reds", cbar_kws={"label": "Attrition rate (%)"},
            linewidths=2, linecolor="white", ax=ax)
ax.set_title("Attrition rate (%): overtime x job satisfaction (1 = low, 4 = high)", fontsize=11, fontweight="bold")
ax.set_xlabel("Job satisfaction")
ax.set_ylabel("Overtime")
save(fig, "09_heatmap_overtime_satisfaction.png")

# 10 key drivers: correlation with attrition
feat = df[["Age", "MonthlyIncome", "JobLevel", "TotalWorkingYears", "YearsAtCompany", "YearsSinceLastPromotion",
           "YearsWithCurrManager", "NumCompaniesWorked", "DistanceFromHome", "JobSatisfaction",
           "WorkLifeBalance", "EnvironmentSatisfaction"]].copy()
feat["Works overtime"] = (df["OverTime"] == "Yes").astype(int)
feat["Travels frequently"] = (df["BusinessTravel"] == "Travel_Frequently").astype(int)
feat["Single"] = (df["MaritalStatus"] == "Single").astype(int)
feat["No stock options"] = (df["StockOptionLevel"] == 0).astype(int)
feat["In Sales"] = (df["Department"] == "Sales").astype(int)
nice = {"MonthlyIncome": "Monthly income", "JobLevel": "Job level", "TotalWorkingYears": "Total experience",
        "YearsAtCompany": "Years at company", "YearsSinceLastPromotion": "Years since promotion",
        "YearsWithCurrManager": "Years with manager", "NumCompaniesWorked": "Companies worked at",
        "DistanceFromHome": "Distance from home", "JobSatisfaction": "Job satisfaction",
        "WorkLifeBalance": "Work-life balance", "EnvironmentSatisfaction": "Environment satisfaction"}
feat = feat.rename(columns=nice)
corr = feat.corrwith(df["AttritionFlag"]).sort_values()
fig, ax = plt.subplots(figsize=(8.5, 6.5))
ax.barh(corr.index, corr.values, color=[RED if v > 0 else BLUE for v in corr.values])
for i, v in enumerate(corr.values):
    ax.text(v + (0.005 if v > 0 else -0.005), i, f"{v:+.2f}", va="center", ha="left" if v > 0 else "right", fontsize=9)
ax.axvline(0, color="black", lw=0.8)
ax.set_xlim(corr.min() - 0.05, corr.max() + 0.05)
ax.set_title("What moves with attrition? (correlation with leaving)", fontsize=12, fontweight="bold", loc="left")
ax.set_xlabel("Correlation with attrition  (red = more likely to leave, blue = less likely)\nCorrelation, not causation")
save(fig, "10_key_drivers.png")

# 12 correlation heatmap
num = df[["Age", "MonthlyIncome", "JobLevel", "TotalWorkingYears", "YearsAtCompany", "YearsSinceLastPromotion",
          "DistanceFromHome", "JobSatisfaction", "WorkLifeBalance", "AttritionFlag"]]
c = num.corr()
mask = np.triu(np.ones_like(c, dtype=bool), k=1)
fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(c, mask=mask, annot=True, fmt=".2f", cmap="coolwarm", center=0, linewidths=0.5, ax=ax,
            cbar_kws={"shrink": 0.8})
ax.set_title("Correlation matrix of numeric features", fontsize=12, fontweight="bold")
save(fig, "12_correlation_heatmap.png")

# 00 dashboard (README hero image)
fig, axes = plt.subplots(2, 2, figsize=(14, 9))
plot_rate(axes[0, 0], "Department", "By department", "")
plot_rate(axes[0, 1], "AgeGroup", "By age group", "")
plot_rate(axes[1, 0], "SalaryBand", "By monthly salary band", "")
plot_rate(axes[1, 1], "OverTime", "By overtime", "")
axes[0, 0].tick_params(axis="x", labelsize=8)
fig.suptitle(f"Employee attrition dashboard  |  overall attrition {overall:.1f}%  (red bars = above average)",
             fontsize=15, fontweight="bold")
save(fig, "00_dashboard.png")

# --------------------------------------------------------------------------- 4. key findings
def rate(mask):
    return df.loc[mask, "AttritionFlag"].mean() * 100


top_drivers = corr.abs().sort_values(ascending=False).head(5).index.tolist()
kf = [
    f"Overall attrition: {overall:.1f}% ({df['AttritionFlag'].sum()} of {len(df):,})",
    f"Overtime: {rate(df['OverTime'] == 'Yes'):.1f}% vs {rate(df['OverTime'] == 'No'):.1f}% without "
    f"({rate(df['OverTime'] == 'Yes') / rate(df['OverTime'] == 'No'):.1f}x)",
    f"Age 18-24: {rate(df['AgeGroup'] == '18-24'):.1f}% | Age 45-54: {rate(df['AgeGroup'] == '45-54'):.1f}%",
    f"Income < 7k: {rate(df['MonthlyIncome'] < 7000):.1f}% | Income >= 12k: {rate(df['MonthlyIncome'] >= 12000):.1f}%",
    f"Experience 0-2 yrs: {rate(df['TotalWorkingYears'] <= 2):.1f}% | 20+ yrs: {rate(df['TotalWorkingYears'] > 20):.1f}%",
    f"Tenure <= 3 yrs: {rate(df['YearsAtCompany'] <= 3):.1f}% | > 3 yrs: {rate(df['YearsAtCompany'] > 3):.1f}%",
    f"Sales dept: {rate(df['Department'] == 'Sales'):.1f}% | rest of company: {rate(df['Department'] != 'Sales'):.1f}%",
    f"Single: {rate(df['MaritalStatus'] == 'Single'):.1f}% | Married: {rate(df['MaritalStatus'] == 'Married'):.1f}%",
    f"No stock options: {rate(df['StockOptionLevel'] == 0):.1f}% | with options: {rate(df['StockOptionLevel'] > 0):.1f}%",
    f"Low job satisfaction (1-2): {rate(df['JobSatisfaction'] <= 2):.1f}% | high (3-4): {rate(df['JobSatisfaction'] >= 3):.1f}%",
    f"Share of all leavers who are under 35: {df.loc[df['AttritionFlag'] == 1, 'Age'].lt(35).mean() * 100:.0f}%",
    f"Share of all leavers working overtime: {(df.loc[df['AttritionFlag'] == 1, 'OverTime'] == 'Yes').mean() * 100:.0f}% "
    f"(overtime is {(df['OverTime'] == 'Yes').mean() * 100:.0f}% of headcount)",
    f"Risk flags 0 / 1 / 2 / 3+: " + " / ".join(f"{rate(df['RiskFlags'] == k):.1f}%" for k in [0, 1, 2]) +
    f" / {rate(df['RiskFlags'] >= 3):.1f}%",
    f"Top-5 correlates of attrition: {', '.join(top_drivers)}",
]
(ROOT / "outputs" / "key_findings.txt").write_text("\n".join(kf), encoding="utf-8")
print("\nKEY FINDINGS\n" + "\n".join(f" - {k}" for k in kf))
print(f"\nCharts saved -> {CHARTS.relative_to(ROOT)}/ ({len(list(CHARTS.glob('*.png')))} files)")
