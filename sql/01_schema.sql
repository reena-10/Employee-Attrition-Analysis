-- Normalised schema: 3 tables so the analysis queries need real JOINs.
DROP TABLE IF EXISTS compensation;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

CREATE TABLE departments (
    dept_id    INTEGER PRIMARY KEY,
    dept_name  TEXT NOT NULL UNIQUE
);

CREATE TABLE employees (
    emp_id                       INTEGER PRIMARY KEY,
    age                          INTEGER NOT NULL,
    gender                       TEXT,
    marital_status               TEXT,
    dept_id                      INTEGER NOT NULL REFERENCES departments(dept_id),
    job_role                     TEXT,
    job_level                    INTEGER,
    total_working_years          INTEGER,
    years_at_company             INTEGER,
    years_since_last_promotion   INTEGER,
    years_with_curr_manager      INTEGER,
    num_companies_worked         INTEGER,
    distance_from_home           INTEGER,
    business_travel              TEXT,
    overtime                     TEXT CHECK (overtime IN ('Yes', 'No')),
    job_satisfaction             INTEGER CHECK (job_satisfaction BETWEEN 1 AND 4),
    work_life_balance            INTEGER CHECK (work_life_balance BETWEEN 1 AND 4),
    environment_satisfaction     INTEGER CHECK (environment_satisfaction BETWEEN 1 AND 4),
    attrition                    TEXT NOT NULL CHECK (attrition IN ('Yes', 'No'))
);

CREATE TABLE compensation (
    emp_id                    INTEGER PRIMARY KEY REFERENCES employees(emp_id),
    monthly_income            INTEGER NOT NULL,
    percent_salary_hike       INTEGER,
    stock_option_level        INTEGER,
    training_times_last_year  INTEGER
);

CREATE INDEX idx_emp_dept ON employees(dept_id);
