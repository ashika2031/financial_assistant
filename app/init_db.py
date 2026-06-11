"""Database initialization: create tables and seed 20+ sample properties + financials."""
import psycopg2
from app.config import DATABASE_URL


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS properties (
    property_id   SERIAL PRIMARY KEY,
    address       TEXT NOT NULL,
    metro_area    TEXT NOT NULL,
    sq_footage    INTEGER NOT NULL,
    property_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS financials (
    id          SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(property_id),
    fiscal_year INTEGER NOT NULL,
    revenue     NUMERIC(14,2) NOT NULL,
    net_income  NUMERIC(14,2) NOT NULL,
    expenses    NUMERIC(14,2) NOT NULL
);
"""

_PROPERTIES = [
    ("100 N Michigan Ave",        "Chicago",        45000,  "Office"),
    ("200 S Wacker Dr",           "Chicago",        62000,  "Office"),
    ("350 W Mart Center",         "Chicago",        38000,  "Industrial"),
    ("1 N State St",              "Chicago",        28000,  "Retail"),
    ("500 W Madison St",          "Chicago",        71000,  "Office"),
    ("123 Main St",               "Los Angeles",    33000,  "Retail"),
    ("456 Wilshire Blvd",         "Los Angeles",    55000,  "Office"),
    ("789 Sunset Blvd",           "Los Angeles",    22000,  "Retail"),
    ("1000 Industrial Pkwy",      "Los Angeles",    88000,  "Industrial"),
    ("321 Commerce Dr",           "Los Angeles",    41000,  "Industrial"),
    ("1 World Trade Center",      "New York",       95000,  "Office"),
    ("350 Fifth Ave",             "New York",       82000,  "Office"),
    ("30 Rockefeller Plaza",      "New York",       74000,  "Office"),
    ("200 Varick St",             "New York",       31000,  "Industrial"),
    ("500 Fashion Ave",           "New York",       26000,  "Retail"),
    ("100 Congress Ave",          "Austin",         19000,  "Office"),
    ("500 Bowie St",              "Austin",         14000,  "Retail"),
    ("200 E 6th St",              "Austin",         11000,  "Retail"),
    ("1500 Tech Ridge Blvd",      "Austin",         67000,  "Industrial"),
    ("2000 E Riverside Dr",       "Austin",         23000,  "Office"),
    ("1 Infinite Loop",           "San Francisco",  48000,  "Office"),
    ("555 Market St",             "San Francisco",  52000,  "Office"),
    ("100 Spear St",              "San Francisco",  37000,  "Office"),
    ("800 Industrial Rd",         "San Francisco",  76000,  "Industrial"),
    ("250 Union Square",          "San Francisco",  18000,  "Retail"),
]

# Revenue multiplier by type
_REV = {"Office": 185, "Retail": 130, "Industrial": 95}
_EXP_RATIO = 0.62
_INC_RATIO  = 0.38


def _financials_for(prop_id: int, sq_ft: int, ptype: str, year: int):
    base = sq_ft * _REV.get(ptype, 150)
    # small year-over-year variance
    factor = 1.0 if year == 2023 else 1.065
    revenue = round(base * factor, 2)
    expenses = round(revenue * _EXP_RATIO, 2)
    net_income = round(revenue * _INC_RATIO, 2)
    return (prop_id, year, revenue, net_income, expenses)


def init_db(force: bool = False) -> dict:
    """Create tables and seed data. Returns status dict."""
    result = {"created_tables": False, "properties_inserted": 0, "financials_inserted": 0, "error": None}
    try:
        conn = psycopg2.connect(DATABASE_URL)
    except Exception as e:
        result["error"] = str(e)
        return result

    try:
        with conn.cursor() as cur:
            cur.execute(_SCHEMA_SQL)
            result["created_tables"] = True

            # check if already seeded
            cur.execute("SELECT COUNT(*) FROM properties;")
            existing = cur.fetchone()[0]
            if existing >= 20 and not force:
                conn.commit()
                result["properties_inserted"] = 0
                result["financials_inserted"] = 0
                return result

            if force:
                cur.execute("DELETE FROM financials;")
                cur.execute("DELETE FROM properties;")

            prop_ids = []
            for addr, metro, sqft, ptype in _PROPERTIES:
                cur.execute(
                    "INSERT INTO properties (address, metro_area, sq_footage, property_type) "
                    "VALUES (%s,%s,%s,%s) RETURNING property_id;",
                    (addr, metro, sqft, ptype)
                )
                prop_ids.append((cur.fetchone()[0], sqft, ptype))
                result["properties_inserted"] += 1

            for pid, sqft, ptype in prop_ids:
                for yr in (2023, 2024):
                    row = _financials_for(pid, sqft, ptype, yr)
                    cur.execute(
                        "INSERT INTO financials (property_id, fiscal_year, revenue, net_income, expenses) "
                        "VALUES (%s,%s,%s,%s,%s);",
                        row
                    )
                    result["financials_inserted"] += 1

        conn.commit()
    except Exception as e:
        conn.rollback()
        result["error"] = str(e)
    finally:
        conn.close()

    return result
