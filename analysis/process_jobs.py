# analysis/process_jobs.py
import pandas as pd
import re
import sqlite3
import os

DB_PATH = "data/jobs.db"

SKILLS = [
    "Python", "SQL", "Power BI", "Excel", "Tableau",
    "R", "Azure", "AWS", "Spark", "Machine Learning",
    "pandas", "NumPy", "Looker", "dbt", "Snowflake"
]

def extract_skills(df):
    """Add a column for each skill — True if mentioned in description."""
    for skill in SKILLS:
        df[skill] = df["description"].str.contains(
            skill, case=False, na=False
        )
    return df

def extract_salary(text):
    """Pull salary numbers out of free text descriptions."""
    if pd.isna(text):
        return None
    # Matches £35,000 or £35k or £35K
    match = re.search(r'£\s?(\d{2,3})[,.]?(\d{3})?', str(text))
    if match:
        if match.group(2):
            return int(match.group(1) + match.group(2))
        val = int(match.group(1))
        return val * 1000 if val < 200 else val
    return None

def process():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM jobs", conn)
    conn.close()

    print(f"Processing {len(df)} jobs...")

    # Extract skills
    df = extract_skills(df)

    # Fill salary from description where min_amount is missing
    df["parsed_salary"] = df["description"].apply(extract_salary)
    df["salary"] = df["min_amount"].combine_first(df["parsed_salary"])

    # Salary band for easier grouping in Power BI
    def salary_band(s):
        if pd.isna(s):       return "Not specified"
        if s < 25000:        return "Under £25k"
        if s < 35000:        return "£25k–£35k"
        if s < 50000:        return "£35k–£50k"
        if s < 70000:        return "£50k–£70k"
        return "£70k+"

    df["salary_band"] = df["salary"].apply(salary_band)

    # Seniority tag
    def seniority(title):
        title = str(title).lower()
        if any(w in title for w in ["junior", "entry", "graduate", "trainee"]):
            return "Junior"
        if any(w in title for w in ["senior", "lead", "principal", "head"]):
            return "Senior"
        return "Mid-level"

    df["seniority"] = df["title"].apply(seniority)

    # Save processed output
    df.to_csv("data/jobs_processed.csv", index=False)
    print(f"Saved to data/jobs_processed.csv")

    # Print skill summary
    print("\n--- Top skills mentioned ---")
    skill_counts = df[SKILLS].sum().sort_values(ascending=False)
    for skill, count in skill_counts.items():
        bar = "█" * int(count / 2)
        print(f"  {skill:<20} {int(count):>3}  {bar}")

    # Print region summary
    print("\n--- Jobs by region ---")
    print(df["region"].value_counts().to_string())

    # Print seniority summary
    print("\n--- Jobs by seniority ---")
    print(df["seniority"].value_counts().to_string())

if __name__ == "__main__":
    process()