"""Utility to setup or reseed the database used by the app.

Usage examples:
  python setup_database.py --health   # print health check
  python setup_database.py --reseed  # reseed 2024 from 2023
  USE_SAMPLE_2024=1 python setup_database.py --reseed
"""
import argparse
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load .env explicitly before importing app modules
_proj_root = Path(__file__).resolve().parent
_env_path = _proj_root / ".env"
load_dotenv(_env_path)

from app.db import health_check, reseed_2024_from_2023
from app.init_db import init_db
from app.config import DATABASE_URL


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--health",  action="store_true", help="Run DB health check")
    parser.add_argument("--init",    action="store_true", help="Create tables and seed 20+ properties")
    parser.add_argument("--force",   action="store_true", help="Force reseed (drops existing data)")
    parser.add_argument("--reseed",  action="store_true", help="Reseed 2024 from 2023")
    parser.add_argument("--dry-run", action="store_true", help="Dry run reseed")
    args = parser.parse_args()

    if not DATABASE_URL:
        print("ERROR: DATABASE_URL is missing.")
        print("Create .env in the project root with DATABASE_URL=postgresql://user:password@host:port/dbname")
        return

    if args.init:
        print("Initializing database schema and seeding sample data...")
        result = init_db(force=args.force)
        print(json.dumps(result, indent=2))
        if result.get("error"):
            print("\nERROR:", result["error"])
        else:
            print(f"\nDone. {result['properties_inserted']} properties and {result['financials_inserted']} financial records inserted.")
        return

    if args.health:
        print("DATABASE_URL is set.")
        h = health_check()
        print(json.dumps(h, indent=2))
        if not h.get("connected"):
            print("\nERROR:", h.get("error"))
            print("Ensure PostgreSQL is running. If using Docker:")
            print("  docker start financial-postgres")
            print("Or create the container:")
            print("  docker run --name financial-postgres \\")
            print("    -e POSTGRES_USER=postgres \\")
            print("    -e POSTGRES_PASSWORD=postgres \\")
            print("    -e POSTGRES_DB=real_estate_db \\")
            print("    -p 5432:5432 \\")
            print("    -d postgres:16")
        return

    if args.reseed:
        # also allow environment variable USE_SAMPLE_2024 to control
        use_sample = os.environ.get("USE_SAMPLE_2024", "0") in ("1", "true", "True")
        if not use_sample:
            print("USE_SAMPLE_2024 not set. Set USE_SAMPLE_2024=1 to allow reseed or pass env var.")
            print("Exiting without reseed.")
            return

        res = reseed_2024_from_2023(dry_run=args.dry_run)
        print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
