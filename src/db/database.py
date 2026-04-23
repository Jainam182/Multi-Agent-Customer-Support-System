import json
import os
import re
import sqlite3
import requests
import logging
from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)

_engine = None
_db = None

# Use project root for the custom SQL file
LOCAL_SQL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ahc_sqlite.sql")

def _load_sql_script() -> str:
    if os.path.isfile(LOCAL_SQL_PATH):
        logger.info(f"Loading Healthcare SQL from local file: {LOCAL_SQL_PATH}")
        with open(LOCAL_SQL_PATH, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise FileNotFoundError(f"Database setup script not found at {LOCAL_SQL_PATH}")


def _create_engine():
    sql_script = _load_sql_script()
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.executescript(sql_script)
    logger.info("Chinook database loaded successfully into memory.")
    return create_engine(
        "sqlite://",
        creator=lambda: connection,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )


def get_engine():
    global _engine
    if _engine is None:
        _engine = _create_engine()
    return _engine


def get_db() -> SQLDatabase:
    global _db
    if _db is None:
        _db = SQLDatabase(get_engine())
    return _db


def run_query_safe(query: str, params: dict = None) -> str:
    engine = get_engine()
    try:
        with engine.connect() as conn:
            if params:
                result = conn.execute(text(query), params)
            else:
                result = conn.execute(text(query))
            rows = result.fetchall()
            columns = result.keys()
            if not rows:
                return "[]"
            results_list = [dict(zip(columns, row)) for row in rows]
            return json.dumps(results_list, default=str)
    except Exception as e:
        logger.error(f"Query error: {e} | query={query} | params={params}")
        raise


def normalize_phone(phone: str) -> str:
    if not phone:
        return ""
    phone = phone.strip()
    if phone.startswith("+"):
        return "+" + re.sub(r"[^\d]", "", phone[1:])
    return re.sub(r"[^\d]", "", phone)


def verify_database() -> dict:
    try:
        db = get_db()
        tables = db.get_usable_table_names()
        result = db.run("SELECT COUNT(*) FROM Customer;")
        logger.info(f"Database verification OK. Customer count query returned: {result}")
        return {"status": "healthy", "tables": len(tables)}
    except Exception as e:
        logger.error(f"Database verification failed: {e}")
        return {"status": "unhealthy", "error": str(e)}
