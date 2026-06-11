from pathlib import Path
from dotenv import load_dotenv
import os

_project_root = Path(__file__).resolve().parents[1]
# Load .env from project root if present
dotenv_path = _project_root / ".env"
load_dotenv(dotenv_path)

# Now read DATABASE_URL from environment (set by .env or user's shell)
DATABASE_URL = os.getenv("DATABASE_URL")

def require_database_url():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not set in environment or .env file")
