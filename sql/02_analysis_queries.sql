-- Attrition analysis queries (SQLite dialect).
-- Each block starts with "-- name: <id>"; src/04_run_sql_analysis.py runs them
-- one by one and saves each result to outputs/sql_results/<id>.csv

-- name: q01_overall_attrition
SELECT COUNT(*)                                                        AS total_employees,
       SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END)              AS leavers,
       ROUND(100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END)
             / COUNT(*), 1)                                            AS attrition_rate_pct
FROM employees;

-- name: q02_attrition_by_department
SELECT d.dept_name                                                     AS department,
       COUNT(*)                                                        AS headcount,
       SUM(CASE WHEN e.attrition = 'Yes' THEN 1 ELSE 0 END)            AS leavers,
       ROUND(100.0 * SUM(CASE WHEN e.attrition = 'Yes' THEN 1 ELSE 0 END)
             / COUNT(*), 1)                                            AS attrition_rate_pct,
       ROUND(AVG(c.monthly_income), 0)                                 AS avg_monthly_income
FROM employees e
JOIN departments  d ON d.dept_id = e.dept_id
JOIN compensation c ON c.emp_id  = e.emp_id
GROUP BY d.dept_name
ORDER BY attrition_rate_pct DESC;

-- name: q03_attrition_by_age_group
SELECT CASE WHEN age < 25 THEN '18-24'
            WHEN age < 35 THEN '25-34'
            WHEN age < 45 THEN '35-44'
            WHEN age < 55 THEN '45-54'
            ELSE '55+' END                                             AS age_group,
       COUNT(*)                                                        AS headcount,
       SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END)              AS leavers,
       ROUND(100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END)
             / COUNT(*), 1)                                            AS attrition_rate_pct
FROM employees
GROUP BY age_group
ORDER BY MIN(age);

-- name: q04_attrition_by_salary_band
SELECT CASE WHEN c.monthly_income < 5000  THEN '1. Under 5,000'
            WHEN c.monthly_income < 7000  THEN '2. 5,000-6,999'
            WHEN c.monthly_income < 9000  THEN '3. 7,000-8,999'
            WHEN c.monthly_income < 12000 THEN '4. 9,000-11,999'
            ELSE '5. 12,000+' END                                      AS salary_band,
       COUNT(*)                                                        AS headcount,
       SUM(CASE WHEN e.attrition = 'Yes' THEN 1 ELSE 0 END)            AS leavers,
       ROUND(100.0 * SUM(CASE WHEN e.attrition = 'Yes' THEN 1 ELSE 0 END)
             / COUNT(*), 1)                                            AS attrition_rate_pct
FROM employees e
JOIN compensation c ON c.emp_id = e.emp_id
GROUP BY salary_band
ORDER BY salary_band;

-- name: q05_attrition_by_experience_band
SELECT CASE WHEN total_working_years <= 2  THEN '1. 0-2 yrs'
            WHEN total_working_years <= 5  THEN '2. 3-5 yrs'
            WHEN total_working_years <= 10 THEN '3. 6-10 yrs'
            WHEN total_working_years <= 20 THEN '4. 11-20 yrs'
            ELSE '5. 20+ yrs' END                                      AS experience_band,
       COUNT(*)                                                        AS headcount,
       SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END)              AS leavers,
       ROUND(100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END)
             / COUNT(*), 1)                                            AS attrition_rate_pct
FROM employees
GROUP BY experience_band
ORDER BY experience_band;

-- name: q06_attrition_by_tenure_band
SELECT CASE WHEN years_at_company <= 1 THEN '1. 0-1 yrs at company'
            WHEN years_at_company <= 3 THEN '2. 2-3 yrs'
            WHEN years_at_company <= 6 THEN '3. 4-6 yrs'
            WHEN years_at_company <= 10 THEN '4. 7-10 yrs'
            ELSE '5. 10+ yrs' END                                      AS tenure_band,
       COUNT(*)                                                        AS headcount,
       ROUND(100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END)
             / COUNT(*), 1)                                            AS attrition_rate_pct
FROM employees
GROUP BY tenure_band
ORDER BY tenure_band;

-- name: q07_overtime_and_travel
SELECT overtime,
       business_travel,
       COUNT(*)                                                        AS headcount,
       ROUND(100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END)
             / COUNT(*), 1)                                            AS attrition_rate_pct
FROM employees
GROUP BY overtime, business_travel
ORDER BY attrition_rate_pct DESC;

-- name: q08_attrition_by_job_role
SELECT d.dept_name  AS department,
       e.job_role,
       COUNT(*)     AS headcount,
       ROUND(100.0 * SUM(CASE WHEN e.attrition = 'Yes' THEN 1 ELSE 0 END)
             / COUNT(*), 1) AS attrition_rate_pct
FROM employees e
JOIN departments d ON d.dept_id = e.dept_id
GROUP BY d.dept_name, e.job_role
HAVING COUNT(*) >= 30
ORDER BY attrition_rate_pct DESC;

-- name: q09_department_by_salary_band
SELECT d.dept_name AS department,
       CASE WHEN c.monthly_income < 5000  THEN 'Low (<5k)'
            WHEN c.monthly_income < 10000 THEN 'Mid (5k-10k)'
            ELSE 'High (10k+)' END                                     AS salary_tier,
       COUNT(*)    AS headcount,
       ROUND(100.0 * SUM(CASE WHEN e.attrition = 'Yes' THEN 1 ELSE 0 END)
             / COUNT(*), 1)                                            AS attrition_rate_pct
FROM employees e
JOIN departments  d ON d.dept_id = e.dept_id
JOIN compensation c ON c.emp_id  = e.emp_id
GROUP BY d.dept_name, salary_tier
HAVING COUNT(*) >= 10
ORDER BY d.dept_name, MIN(c.monthly_income);

-- name: q10_leavers_vs_stayers_profile
SELECT e.attrition,
       COUNT(*)                              AS headcount,
       ROUND(AVG(e.age), 1)                  AS avg_age,
       ROUND(AVG(c.monthly_income), 0)       AS avg_monthly_income,
       ROUND(AVG(e.years_at_company), 1)     AS avg_years_at_company,
       ROUND(AVG(e.distance_from_home), 1)   AS avg_distance_km,
       ROUND(AVG(e.job_satisfaction), 2)     AS avg_job_satisfaction,
       ROUND(AVG(e.work_life_balance), 2)    AS avg_work_life_balance
FROM employees e
JOIN compensation c ON c.emp_id = e.emp_id
GROUP BY e.attrition;

-- name: q11_risk_flag_score
-- Count how many risk flags each employee carries and compare attrition by score.
WITH flagged AS (
    SELECT e.emp_id,
           e.attrition,
           CASE WHEN e.overtime = 'Yes'          THEN 1 ELSE 0 END AS f_overtime,
           CASE WHEN e.job_satisfaction <= 2     THEN 1 ELSE 0 END AS f_low_satisfaction,
           CASE WHEN c.monthly_income < 5000     THEN 1 ELSE 0 END AS f_low_income,
           CASE WHEN e.years_at_company <= 2     THEN 1 ELSE 0 END AS f_new_hire
    FROM employees e
    JOIN compensation c ON c.emp_id = e.emp_id
)
SELECT f_overtime + f_low_satisfaction + f_low_income + f_new_hire     AS risk_flags,
       COUNT(*)                                                        AS headcount,
       SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END)              AS leavers,
       ROUND(100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END)
             / COUNT(*), 1)                                            AS attrition_rate_pct
FROM flagged
GROUP BY risk_flags
ORDER BY risk_flags;
