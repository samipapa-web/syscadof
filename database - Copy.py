# database.py
#------------------------------------------------------------------
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# =========================================================
# CONFIGURATION POSTGRESQL
# =========================================================
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

def get_connection():
    """
    Retourne une connexion PostgreSQL avec des résultats sous forme de dictionnaire.
    """
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    return conn