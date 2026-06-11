"""Simple CLI helper to reseed 2024 sample rows.

This will set USE_SAMPLE_2024=1 for the subprocess and call setup_database.py --reseed
"""
import subprocess
import os
import sys


def main():
    env = os.environ.copy()
    env["USE_SAMPLE_2024"] = "1"
    cmd = [sys.executable, "setup_database.py", "--reseed"]
    subprocess.run(cmd, env=env)


if __name__ == "__main__":
    main()
