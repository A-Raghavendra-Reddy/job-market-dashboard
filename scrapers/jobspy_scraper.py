# scrapers/jobspy_scraper.py
import requests
import pandas as pd
from datetime import date
import os
import time
from dotenv import load_dotenv

load_dotenv()

# ── Adzuna credentials (free at developer.adzuna.com) ──────────────────────
ADZUNA_APP_ID  = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_API_KEY")


# ── 1. Adzuna scraper (UK jobs, best coverage) ─────────────────────────────
def scrape_adzuna(keyword="data analyst", pages=3):
    print("Scraping Adzuna...")
    all_jobs = []

    for page in range(1, pages + 1):
        url = f"https://api.adzuna.com/v1/api/jobs/gb/search/{page}"
        params = {
            "app_id":           ADZUNA_APP_ID,
            "app_key":          ADZUNA_APP_KEY,
            "results_per_page": 50,
            "what":             keyword,
            "content-type":     "application/json"
        }
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"  Adzuna page {page} failed: {response.status_code}")
            break

        jobs = response.json().get("results", [])
        all_jobs.extend(jobs)
        print(f"  Page {page}: {len(jobs)} jobs fetched")
        time.sleep(1)   # be polite, avoid rate limiting

    if not all_jobs:
        return pd.DataFrame()

    rows = []
    for job in all_jobs:
        rows.append({
            "title":       job.get("title", ""),
            "company":     job.get("company", {}).get("display_name", ""),
            "location":    job.get("location", {}).get("display_name", ""),
            "description": job.get("description", ""),
            "min_amount":  job.get("salary_min"),
            "max_amount":  job.get("salary_max"),
            "date_posted": job.get("created"),
            "job_url":     job.get("redirect_url", ""),
            "site":        "adzuna"
        })

    return pd.DataFrame(rows)


# ── 2. Remotive scraper (remote jobs, no key needed) ───────────────────────
def scrape_remotive(keyword="data analyst"):
    print("Scraping Remotive...")
    url    = "https://remotive.com/api/remote-jobs"
    params = {"search": keyword, "limit": 50}

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"  Remotive failed: {response.status_code}")
        return pd.DataFrame()

    jobs = response.json().get("jobs", [])
    rows = []
    for job in jobs:
        rows.append({
            "title":       job.get("title", ""),
            "company":     job.get("company_name", ""),
            "location":    "Remote",
            "description": job.get("description", ""),
            "min_amount":  None,
            "max_amount":  None,
            "date_posted": job.get("publication_date"),
            "job_url":     job.get("url", ""),
            "site":        "remotive"
        })

    print(f"  {len(rows)} jobs fetched")
    return pd.DataFrame(rows)


# ── 3. The Muse scraper (no key needed) ────────────────────────────────────
def scrape_the_muse(keyword="data analyst"):
    print("Scraping The Muse...")
    url    = "https://www.themuse.com/api/public/jobs"
    params = {"category": "Data Science", "level": "Entry Level", "page": 1}

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"  The Muse failed: {response.status_code}")
        return pd.DataFrame()

    jobs = response.json().get("results", [])
    rows = []
    for job in jobs:
        locations = job.get("locations", [{}])
        rows.append({
            "title":       job.get("name", ""),
            "company":     job.get("company", {}).get("name", ""),
            "location":    locations[0].get("name", "") if locations else "",
            "description": " ".join(
                            [c.get("body","") for c in job.get("contents","")]
                           ) if job.get("contents") else "",
            "min_amount":  None,
            "max_amount":  None,
            "date_posted": job.get("publication_date"),
            "job_url":     job.get("refs", {}).get("landing_page", ""),
            "site":        "the_muse"
        })

    print(f"  {len(rows)} jobs fetched")
    return pd.DataFrame(rows)


# ── Cleaning ────────────────────────────────────────────────────────────────
def clean_jobs(df):
    df = df.copy()
    df["scraped_date"] = date.today()
    df = df.dropna(subset=["title", "company"])
    df = df[df["title"].str.strip() != ""]

    # Standardise region
    def get_region(loc):
        if pd.isna(loc): return "Unknown"
        loc = str(loc).lower()
        if "london"     in loc: return "London"
        if "manchester" in loc: return "Manchester"
        if "birmingham" in loc: return "Birmingham"
        if "leeds"      in loc: return "Leeds"
        if "edinburgh"  in loc or "glasgow" in loc: return "Scotland"
        if "remote"     in loc: return "Remote"
        return "Other UK"

    df["region"]    = df["location"].apply(get_region)
    df["is_remote"] = df["location"].str.contains("remote", case=False, na=False)

    return df.drop_duplicates(subset=["title", "company"])


# ── Main ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    frames = []

    adzuna  = scrape_adzuna()
    remotive = scrape_remotive()
    muse    = scrape_the_muse()

    for df in [adzuna, remotive, muse]:
        if not df.empty:
            frames.append(df)

    if not frames:
        print("\nNo data collected. Check your Adzuna credentials in .env")
    else:
        combined = pd.concat(frames, ignore_index=True)
        cleaned  = clean_jobs(combined)

        os.makedirs("data", exist_ok=True)
        cleaned.to_csv("data/jobs_raw.csv", index=False)

        print(f"\n{'─'*40}")
        print(f"Total jobs collected : {len(combined)}")
        print(f"After deduplication  : {len(cleaned)}")
        print(f"Saved to             : data/jobs_raw.csv")
        print(f"{'─'*40}\n")
        print(cleaned[["title", "company", "region", "site"]].head(10).to_string(index=False))
