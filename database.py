# database.py
# ----------------------------------------------------------

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

# =========================================================
# ENV SAFE
# =========================================================
def _env(name, default=None, required=True):
    value = os.getenv(name, default)
    if required and not value:
        raise EnvironmentError(f"Variable manquante : {name}")
    return value

DB_CONFIG = {
    "host": _env("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": _env("DB_NAME"),
    "user": _env("DB_USER"),
    "password": _env("DB_PASSWORD")
}

# =========================================================
# POOL
# =========================================================
pool = SimpleConnectionPool(1, 20, **DB_CONFIG)

def get_connection():
    return pool.getconn()

def release_connection(conn):
    if conn:
        pool.putconn(conn)

def get_cursor(conn):
    return conn.cursor(cursor_factory=RealDictCursor)
