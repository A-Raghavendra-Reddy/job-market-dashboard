Live Job Market Analytics Dashboard
github.com/A-Raghavendra-Reddy/job-market-dashboard
Python  |  SQLite  |  Power BI  |  GitHub Actions  |  Adzuna API
Overview:
An automated job market intelligence system that scrapes 150+ UK Data Analyst job postings daily, tracks skill demand trends, salary patterns, and geographic distribution — visualised in a live Power BI dashboard connected directly to GitHub.
What It Does
•	Scrapes 150+ Data Analyst job postings daily across the UK using the Adzuna API
•	Stores historical data in SQLite — builds trend data over time with zero duplicates
•	Extracts skill demand frequency: SQL, Python, Power BI, Excel, Tableau, Azure, Spark, ML
•	Classifies jobs by region, seniority level, and salary band automatically
•	Visualises all data in a live Power BI dashboard connected to GitHub
•	Runs automatically every morning at 7am UTC via GitHub Actions — zero manual steps
Tech Stack
Scraping	Python, Adzuna API
Storage	SQLite, CSV
Processing	pandas, regex
Visualisation	Power BI Desktop
Automation	GitHub Actions (cron schedule — daily 7am UTC)
Version Control	Git, GitHub
Dashboard Visuals
Visual	Description
KPI Cards	Total jobs, avg salary, remote roles, SQL demand
Skill Frequency Bar	Top 8 skills ranked by mention count in job descriptions
Jobs by Region Donut	London vs Manchester vs Remote vs Other UK
Jobs Over Time Line	Daily posting trend — grows with each pipeline run
Salary Distribution	Jobs grouped by salary band (Under £25k to £70k+)
Interactive Slicers	Filter entire dashboard by region, seniority, data source
Project Structure
job-market-dashboard/ ├── scrapers/ │   └── jobspy_scraper.py       # Adzuna API scraper ├── analysis/ │   ├── save_to_db.py           # SQLite storage + deduplication │   └── process_jobs.py         # Skill extraction, salary parsing ├── data/ │   ├── jobs_raw.csv            # Today's raw scrape │   ├── jobs_export.csv         # Full database export │   └── jobs_processed.csv      # Enriched data (Power BI reads this) ├── .github/workflows/ │   └── daily_scrape.yml        # GitHub Actions automation ├── run_pipeline.py             # Run full pipeline in one command └── Job_live_dashboard.pbix     # Power BI dashboard file
Automation Flow
The pipeline runs automatically every day at 7am UTC via GitHub Actions:
•	GitHub Actions wakes up on cron schedule (0 7 * * *)
•	Scrapes 150+ jobs from Adzuna API across all UK regions
•	Saves only new jobs to SQLite database — deduplication by job URL
•	Extracts skills, salary bands, seniority tags using pandas and regex
•	Commits updated jobs_processed.csv back to GitHub repository
•	Power BI reads fresh CSV from raw GitHub URL on next Refresh click
How to Run Locally
1. Clone the repo
git clone https://github.com/A-Raghavendra-Reddy/job-market-dashboard.git
2. Install dependencies
pip install -r requirements.txt
3. Add Adzuna credentials to .env
ADZUNA_APP_ID=your_id ADZUNA_API_KEY=your_key
4. Run the pipeline
python run_pipeline.py
Sample Findings
•	Most demanded skill: SQL — mentioned in 77% of postings
•	Power BI demand growing week-on-week across UK postings
•	Geographic split: ~43% London, ~35% Other UK, ~16% Remote
•	Average advertised salary: £46,530

