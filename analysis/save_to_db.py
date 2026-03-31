# analysis/save_to_db.py
import sqlite3
import pandas as pd
import os
from datetime import date

DB_PATH = "data/jobs.db"

def create_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            title           TEXT,
            company         TEXT,
            location        TEXT,
            region          TEXT,
            is_remote       BOOLEAN,
            description     TEXT,
            min_amount      REAL,
            max_amount      REAL,
            date_posted     TEXT,
            job_url         TEXT,
            site            TEXT,
            scraped_date    TEXT
        )
    """)
    conn.commit()

def load_existing(conn):
    """Load already-saved job URLs so we don't insert duplicates."""
    try:
        existing = pd.read_sql("SELECT job_url FROM jobs", conn)
        return set(existing["job_url"].tolist())
    except:
        return set()

def save_to_db(df):
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    create_table(conn)

    # Only insert jobs we haven't seen before (matched by URL)
    existing_urls = load_existing(conn)
    new_jobs = df[~df["job_url"].isin(existing_urls)].copy()

    if new_jobs.empty:
        print("No new jobs to add — all already in database.")
        conn.close()
        return

    new_jobs.to_sql("jobs", conn, if_exists="append", index=False)
    conn.commit()

    total = pd.read_sql("SELECT COUNT(*) as count FROM jobs", conn).iloc[0]["count"]
    conn.close()

    print(f"New jobs added     : {len(new_jobs)}")
    print(f"Total in database  : {int(total)}")

def export_for_powerbi():
    """Export full database to CSV — Power BI reads this file."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM jobs", conn)
    conn.close()

    df.to_csv("data/jobs_export.csv", index=False)
    print(f"Exported {len(df)} rows to data/jobs_export.csv")
    return df

if __name__ == "__main__":
    # Load today's scraped data
    if not os.path.exists("data/jobs_raw.csv"):
        print("No jobs_raw.csv found. Run jobspy_scraper.py first.")
        exit()

    df = pd.read_csv("data/jobs_raw.csv")
    print(f"Loaded {len(df)} jobs from jobs_raw.csv")

    # Save to database
    print("\nSaving to database...")
    save_to_db(df)

    # Export for Power BI
    print("\nExporting for Power BI...")
    export_for_powerbi()

    print("\nDone! Check data/jobs_export.csv")