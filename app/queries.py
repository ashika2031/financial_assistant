"""SQL query helpers for properties and financials."""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from app.config import DATABASE_URL


def _conn():
    return psycopg2.connect(DATABASE_URL)


def get_properties(metro_area: Optional[str] = None, property_type: Optional[str] = None) -> List[Dict]:
    sql = "SELECT * FROM properties WHERE 1=1"
    params = []
    if metro_area:
        sql += " AND LOWER(metro_area) LIKE LOWER(%s)"
        params.append(f"%{metro_area}%")
    if property_type:
        sql += " AND LOWER(property_type) = LOWER(%s)"
        params.append(property_type)
    sql += " ORDER BY property_id;"
    try:
        with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]
    except Exception:
        return []


def get_financials(fiscal_year: Optional[int] = None, property_id: Optional[int] = None) -> List[Dict]:
    sql = """
        SELECT f.*, p.address, p.metro_area, p.property_type, p.sq_footage
        FROM financials f
        JOIN properties p USING (property_id)
        WHERE 1=1
    """
    params = []
    if fiscal_year:
        sql += " AND f.fiscal_year = %s"
        params.append(fiscal_year)
    if property_id:
        sql += " AND f.property_id = %s"
        params.append(property_id)
    sql += " ORDER BY f.fiscal_year, p.property_id;"
    try:
        with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]
    except Exception:
        return []


def get_summary(fiscal_year: Optional[int] = None) -> Dict[str, Any]:
    sql = """
        SELECT
            COUNT(DISTINCT property_id)  AS property_count,
            SUM(revenue)                 AS total_revenue,
            SUM(net_income)              AS total_net_income,
            SUM(expenses)                AS total_expenses
        FROM financials
        WHERE 1=1
    """
    params = []
    if fiscal_year:
        sql += " AND fiscal_year = %s"
        params.append(fiscal_year)
    try:
        with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else {}
    except Exception:
        return {}


def get_metro_breakdown(fiscal_year: int) -> List[Dict]:
    sql = """
        SELECT p.metro_area,
               SUM(f.revenue)    AS revenue,
               SUM(f.net_income) AS net_income,
               SUM(f.expenses)   AS expenses,
               COUNT(*)          AS properties
        FROM financials f
        JOIN properties p USING (property_id)
        WHERE f.fiscal_year = %s
        GROUP BY p.metro_area
        ORDER BY revenue DESC;
    """
    try:
        with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (fiscal_year,))
            return [dict(r) for r in cur.fetchall()]
    except Exception:
        return []


def get_type_breakdown(fiscal_year: int) -> List[Dict]:
    sql = """
        SELECT p.property_type,
               SUM(f.revenue)    AS revenue,
               SUM(f.net_income) AS net_income,
               SUM(f.expenses)   AS expenses,
               COUNT(*)          AS properties
        FROM financials f
        JOIN properties p USING (property_id)
        WHERE f.fiscal_year = %s
        GROUP BY p.property_type
        ORDER BY revenue DESC;
    """
    try:
        with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (fiscal_year,))
            return [dict(r) for r in cur.fetchall()]
    except Exception:
        return []
