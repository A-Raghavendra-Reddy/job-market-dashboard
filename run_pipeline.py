# run_pipeline.py
import subprocess
import sys

python = sys.executable   # uses the same venv Python automatically

print("=" * 40)
print("   Job Market Pipeline")
print("=" * 40)

print("\nStep 1: Scraping jobs...")
result = subprocess.run([python, "scrapers/jobspy_scraper.py"])
if result.returncode != 0:
    print("Scraper failed. Fix errors above before continuing.")
    sys.exit(1)

print("\nStep 2: Saving to database...")
result = subprocess.run([python, "analysis/save_to_db.py"])
if result.returncode != 0:
    print("Database save failed. Fix errors above before continuing.")
    sys.exit(1)

print("\nStep 3: Processing insights...")
result = subprocess.run([python, "analysis/process_jobs.py"])
if result.returncode != 0:
    print("Processing failed. Fix errors above before continuing.")
    sys.exit(1)

print("\n" + "=" * 40)
print("Pipeline complete!")
print("Power BI file ready: data/jobs_processed.csv")
print("=" * 40)