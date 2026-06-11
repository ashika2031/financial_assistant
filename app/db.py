import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
from app.config import DATABASE_URL
from typing import Dict, Any, List


def _connect():
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is missing. Create .env in the project root with:\n"
            "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/real_estate_db"
        )
    try:
        return psycopg2.connect(DATABASE_URL)
    except psycopg2.OperationalError as e:
        raise RuntimeError(
            f"PostgreSQL connection failed: {e}\n"
            "Ensure PostgreSQL is running. If using Docker:\n"
            "  docker start financial-postgres\n"
            "Or create the container:\n"
            "  docker run --name financial-postgres -e POSTGRES_USER=postgres "
            "-e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=real_estate_db "
            "-p 5432:5432 -d postgres:16"
        )


def health_check() -> Dict[str, Any]:
    """Return a dictionary describing DB health: connection, tables existence, row counts, fiscal years.

    Keys:
      - connected: bool
      - properties_exists: bool
      - financials_exists: bool
      - properties_count: int
      - financials_count: int
      - fiscal_years: List[int]
      - error: optional error string
    """
    out: Dict[str, Any] = {
        "connected": False,
        "properties_exists": False,
        "financials_exists": False,
        "properties_count": 0,
        "financials_count": 0,
        "fiscal_years": [],
        "error": None,
    }
    try:
        conn = _connect()
        out["connected"] = True
    except Exception as e:
        out["error"] = f"connect: {e}"
        return out

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # check tables exist
            cur.execute("""
            SELECT tablename FROM pg_catalog.pg_tables
            WHERE schemaname NOT IN ('pg_catalog','information_schema');
            """)
            tables = {r["tablename"] for r in cur.fetchall()}
            out["properties_exists"] = "properties" in tables
            out["financials_exists"] = "financials" in tables

            if out["properties_exists"]:
                cur.execute('SELECT COUNT(*) AS cnt FROM properties;')
                out["properties_count"] = int(cur.fetchone()["cnt"])

            if out["financials_exists"]:
                cur.execute('SELECT COUNT(*) AS cnt FROM financials;')
                out["financials_count"] = int(cur.fetchone()["cnt"])
                # fiscal years
                cur.execute('SELECT DISTINCT fiscal_year FROM financials ORDER BY fiscal_year;')
                rows = cur.fetchall()
                yrs = [int(r["fiscal_year"]) for r in rows if r["fiscal_year"] is not None]
                out["fiscal_years"] = yrs

    except Exception as e:
        out["error"] = f"query: {e}"
    finally:
        try:
            conn.close()
        except Exception:
            pass

    return out


def reseed_2024_from_2023(dry_run: bool = False) -> Dict[str, Any]:
    """Copy financials from 2023 to 2024 with updated fiscal_year=2024.

    Returns dict with inserted count and status.
    """
    result = {"inserted": 0, "status": "ok", "error": None}
    try:
        conn = _connect()
    except Exception as e:
        result["status"] = "error"
        result["error"] = f"connect: {e}"
        return result

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # ensure financials exists
            cur.execute("SELECT to_regclass('public.financials') IS NOT NULL AS exists;")
            if not cur.fetchone()["exists"]:
                result["status"] = "error"
                result["error"] = "financials table does not exist"
                return result

            # select 2023 rows
            cur.execute('SELECT * FROM financials WHERE fiscal_year = %s;', (2023,))
            rows = cur.fetchall()
            if not rows:
                result["status"] = "error"
                result["error"] = "no 2023 rows to copy"
                return result

            # build insert for each row, changing fiscal_year to 2024
            # We'll use column list from cursor description
            cols = [d.name for d in cur.description]
            if "fiscal_year" not in cols:
                result["status"] = "error"
                result["error"] = "financials table has no fiscal_year column"
                return result

            cols_noid = cols.copy()
            # remove primary keys if present like id to avoid conflicts; assume 'id' is PK
            if "id" in cols_noid:
                cols_noid.remove("id")

            col_sql = ",".join(cols_noid)
            placeholders = ",".join(["%s"] * len(cols_noid))

            insert_sql = f"INSERT INTO financials ({col_sql}) VALUES ({placeholders});"

            if dry_run:
                result["inserted"] = len(rows)
                result["status"] = "dry_run"
                return result

            inserted = 0
            for r in rows:
                vals = []
                for c in cols_noid:
                    if c == "fiscal_year":
                        vals.append(2024)
                    else:
                        vals.append(r.get(c))
                cur.execute(insert_sql, vals)
                inserted += 1

            conn.commit()
            result["inserted"] = inserted

    except Exception as e:
        conn.rollback()
        result["status"] = "error"
        result["error"] = str(e)
    finally:
        try:
            conn.close()
        except Exception:
            pass

    return result


def is_fiscal_year_available(year: int) -> bool:
    """Return True if the given fiscal year exists in financials."""
    try:
        conn = _connect()
    except Exception:
        return False

    try:
        with conn.cursor() as cur:
            cur.execute('SELECT EXISTS (SELECT 1 FROM financials WHERE fiscal_year = %s LIMIT 1);', (year,))
            exists = cur.fetchone()[0]
            return bool(exists)
    except Exception:
        return False
    finally:
        try:
            conn.close()
        except Exception:
            pass


def year_missing_message(year: int) -> Dict[str, Any]:
    """Return a dict with message and available years when the requested year is missing.

    Returns:
      {"ok": False, "message": str, "available_years": List[int]}
    """
    h = health_check()
    yrs = h.get("fiscal_years", []) if h else []
    msg = f"No records are available for {year}. Available fiscal years are: {yrs}."
    return {"ok": False, "message": msg, "available_years": yrs}
