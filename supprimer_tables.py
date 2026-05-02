# ========================================
# supprimer_tables.py
# ========================================

import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
import json
import os
import config

# =========================================================
# CONFIGURATION DB
# =========================================================
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

# =========================================================
# CONNEXION
# =========================================================
def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# =========================================================
# RESET DES TABLES (si besoin)
# =========================================================
def reset_tables(conn):
    tables = [
        "sources_lac"
    ]
    
#        "sources_lac",
#       "sources_clean",
#        "base_scripts",
#        "restitution",
#        "notification"
        
    cur = conn.cursor()
    for table in tables:
        try:
            cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
            print(f"🗑️ Table supprimée : {table}")
        except Exception as e:
            print(f"⚠️ Erreur suppression table {table} : {e}")
    conn.commit()
    cur.close()
    print("⚠️ RESET ACTIVÉ")
    
conn = get_connection()
reset_tables(conn)