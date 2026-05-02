# ========================================
# init_database.py complet et modulaire
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
# OUTILS
# =========================================================
def to_bool(value):
    return str(value).strip().lower() in ["oui", "yes", "true", "1"]

# =========================================================
# FONCTION GENERIQUE DE CHARGEMENT D'UNE FEUILLE
# =========================================================
def load_sheet_to_db(conn, sheet_name, table_name, columns, unique, transform, update=None, chunk_size=50):
    path = config.REF_PATH
    if not os.path.exists(path):
        print(f"⚠️ Fichier {path} introuvable")
        return

    try:
        df = pd.read_excel(path, sheet_name=sheet_name)
    except Exception:
        print(f"⚠️ Feuille {sheet_name} introuvable")
        return

    df.columns = [col.strip() for col in df.columns]
    values = [transform(row) for _, row in df.iterrows()]

    if not values:
        print(f"⚠️ Aucun enregistrement dans {sheet_name}")
        return

    insert_query = f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES %s
        ON CONFLICT {unique}
    """
    if update:
        insert_query += f" DO UPDATE SET {update}"
    else:
        insert_query += " DO NOTHING"

    cur = conn.cursor()
    for i in range(0, len(values), chunk_size):
        chunk = values[i:i+chunk_size]
        execute_values(cur, insert_query, chunk)
    cur.close()
    print(f"✅ {sheet_name} chargé ({len(values)} lignes)")

# =========================================================
# RESET DES TABLES (si besoin)
# =========================================================
def reset_tables(conn):
    tables = [
        "niu"
    ]
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

# =========================================================
# INITIALISATION DES TABLES
# =========================================================
def init_database():
    try:
        conn = get_connection()

        # ----- RESET tables -----
        reset_tables(conn)

        cursor = conn.cursor()

        # ----- Commandes SQL pour créer les tables -----
        commands = [
            """
            CREATE TABLE niu (
                id SERIAL PRIMARY KEY,
                niu TEXT NOT NULL,
                raison_sociale TEXT,
                sigle TEXT,
                activite TEXT,
                regime TEXT,
                centre TEXT,
                etat TEXT,
                telephone TEXT,
                UNIQUE(niu)
            );
            """            
        ]

        for cmd in commands:
            cursor.execute(cmd)
        conn.commit()

        # ----- Configuration des feuilles Excel -----
        sheets_config = {
            "NIU": {
                "table": "niu",
                "columns": ["niu", "raison_sociale", "sigle", "activite", "regime", "centre", "etat", "telephone"],
                "unique": "(niu)",
                "transform": lambda row: (
                    str(row["NIU"]).strip(),
                    str(row["RAISON_SOCIALE"]).strip(),
                    str(row["SIGLE"]).strip(),
                    str(row["ACTIVITE"]).strip(),
                    str(row["REGIME"]).strip(),
                    str(row["CENTRE"]).strip(),
                    str(row["ETAT"]).strip(),
                    str(row["TELEPHONE"]).strip()
                )
            }
        }

        # ----- Chargement Excel → DB avec commit intermédiaire -----
        for sheet_name, cfg in sheets_config.items():
            load_sheet_to_db(
                conn,
                sheet_name,
                cfg["table"],
                cfg["columns"],
                cfg["unique"],
                cfg["transform"],
                cfg.get("update"),
                chunk_size=100
            )
#            conn.commit()  # commit après chaque table

        conn.close()
        print("✅ Base PostgreSQL initialisée complètement")

    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation : {e}")

# =========================================================
# POINT D’ENTRÉE
# =========================================================
if __name__ == "__main__":
    print("Lancement de l'initialisation de la base...")
    run_init = init_database
    run_init()
    