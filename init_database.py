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
def load_sheet_to_db(conn, sheet_name, table_name, columns, unique, transform, update=None, chunk_size=1000):
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
        "users", "roles", "risques", "notifs",
        "matieres", "cri", "centre", "ug",
         "niu", "sources_donnees"
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
            CREATE TABLE roles (
                id SERIAL PRIMARY KEY,
                role_name TEXT UNIQUE NOT NULL,
                permissions JSONB NOT NULL
            );
            """,
            """
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role_name TEXT REFERENCES roles(role_name)
            );
            """,
            """
            CREATE TABLE risques (
                id SERIAL PRIMARY KEY,
                chapitre TEXT NOT NULL,
                risque TEXT NOT NULL,
                axe TEXT NOT NULL,
                UNIQUE(chapitre, risque, axe)
            );
            """,
            """
            CREATE TABLE notifs (
                id SERIAL PRIMARY KEY,
                type_notification TEXT NOT NULL,
                modele_notification TEXT NOT NULL,
                UNIQUE(type_notification, modele_notification)
            );
            """,
            """
            CREATE TABLE matieres (
                id SERIAL PRIMARY KEY,
                matiere_recoupee TEXT NOT NULL,
                UNIQUE(matiere_recoupee)
            );
            """,
            """
            CREATE TABLE cri (
                id SERIAL PRIMARY KEY,
                cri TEXT NOT NULL,
                UNIQUE(cri)
            );
            """,
            """
            CREATE TABLE centre (
                id SERIAL PRIMARY KEY,
                centre TEXT NOT NULL,
                UNIQUE(centre)
            );
            """,
            """
            CREATE TABLE ug (
                id SERIAL PRIMARY KEY,
                centre TEXT NOT NULL,
                cri TEXT,
                cdif TEXT,
                crif TEXT,
                cdia TEXT,
                cria TEXT,
                acdi TEXT,
                acri TEXT,
                ville TEXT,
                directeur TEXT,
                regional TEXT,
                UNIQUE(centre)
            );
            """,
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
            """,
            """
            CREATE TABLE sources_donnees (
                id SERIAL PRIMARY KEY,
                intitule_source TEXT NOT NULL,
                provenance TEXT NOT NULL CHECK (provenance IN ('Interne', 'Externe')),
                fournisseur TEXT NOT NULL,
                categorie TEXT NOT NULL,
                temporalite TEXT NOT NULL CHECK (temporalite IN ('Stock', 'Flux annuel', 'Flux mensuel')),
                type_fichier TEXT,
                actif INTEGER NOT NULL DEFAULT 1,
                UNIQUE(intitule_source, fournisseur, temporalite)
            );
            """,
            """            
            CREATE TABLE IF NOT EXISTS sources_lac (
                id SERIAL PRIMARY KEY,
                source_id INTEGER NOT NULL,
                intitule_source TEXT NOT NULL,
                provenance TEXT NOT NULL,
                fournisseur TEXT NOT NULL,
                categorie TEXT NOT NULL,
                temporalite TEXT NOT NULL,
                annee INTEGER NOT NULL,
                mois INTEGER DEFAULT 0,
                type_fichier TEXT NOT NULL,
                chemin TEXT NOT NULL,
                nom_fichier TEXT NOT NULL,
                taille INTEGER,
                hash_fichier TEXT,
                utilisateur TEXT NOT NULL,
                date_stockage TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS sources_clean (
                id SERIAL PRIMARY KEY,
                source_id INTEGER NOT NULL,
                intitule_source TEXT NOT NULL,
                provenance TEXT NOT NULL,
                fournisseur TEXT NOT NULL,
                categorie TEXT NOT NULL,
                temporalite TEXT NOT NULL,
                annee INTEGER NOT NULL,
                mois INTEGER DEFAULT 0,
                type_fichier TEXT NOT NULL,
                chemin TEXT NOT NULL,
                nom_fichier TEXT NOT NULL,
                taille INTEGER,
                hash_fichier TEXT,
                utilisateur TEXT NOT NULL,
                date_stockage TEXT NOT NULL,
                date_apurement TEXT,       -- pour log traitement
                script_utilise TEXT,       -- script qui a traité la source
                statut TEXT                -- Succès ou Erreur
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS base_scripts (
                id SERIAL PRIMARY KEY,
                titre TEXT NOT NULL,
                object TEXT NOT NULL,
                auteur TEXT NOT NULL,
                chemin_script TEXT NOT NULL,
                date_stockage TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS restitution (
                id SERIAL PRIMARY KEY,
                nom_fichier TEXT,
                chapitre TEXT,
                risque TEXT,
                axe TEXT,
                script_utilise TEXT,
                utilisateur TEXT,
                impots_inclus TEXT,
                date_generation TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS notification (
                id SERIAL PRIMARY KEY,
                notification TEXT,
                nom_fichier TEXT,
                type_notification TEXT,
                script_utilise TEXT,
                utilisateur TEXT,
                date_creation TEXT
            );
            """            
        ]

        for cmd in commands:
            cursor.execute(cmd)
        conn.commit()

        # ----- Configuration des feuilles Excel -----
        sheets_config = {
            "SOURCES": {
                "table": "sources_donnees",
                "columns": ["intitule_source", "provenance", "fournisseur", "categorie", "temporalite"],
                "unique": "(intitule_source, fournisseur, temporalite)",
                "transform": lambda row: (
                    str(row["intitule_source"]).strip(),
                    str(row["provenance"]).strip(),
                    str(row["fournisseur"]).strip(),
                    str(row["categorie"]).strip(),
                    str(row["temporalite"]).strip()
                )
            },
            "ROLES": {
                "table": "roles",
                "columns": ["role_name", "permissions"],
                "unique": "(role_name)",
                "transform": lambda row: (
                    str(row["Role"]).strip(),
                    json.dumps({col: to_bool(row[col]) for col in row.index if col != "Role"})
                ),
                "update": "permissions = EXCLUDED.permissions"
            },
            "USERS": {
                "table": "users",
                "columns": ["username", "password", "role_name"],
                "unique": "(username)",
                "transform": lambda row: (
                    str(row["Utilisateur"]).strip(),
                    str(row["Mot de passe"]).strip(),
                    str(row["Role"]).strip()
                ),
                "update": "password = EXCLUDED.password, role_name = EXCLUDED.role_name"
            },
            "RISQUES": {
                "table": "risques",
                "columns": ["chapitre", "risque", "axe"],
                "unique": "(chapitre, risque, axe)",
                "transform": lambda row: (
                    str(row["CHAPITRE"]).strip(),
                    str(row["RISQUE"]).strip(),
                    str(row["AXE"]).strip()
                )
            },
            "NOTIFS": {
                "table": "notifs",
                "columns": ["type_notification", "modele_notification"],
                "unique": "(type_notification, modele_notification)",
                "transform": lambda row: (
                    str(row["Type_notification"]).strip(),
                    str(row["Modele_notification"]).strip()
                )
            },
            "MATIERES": {
                "table": "matieres",
                "columns": ["matiere_recoupee"],
                "unique": "(matiere_recoupee)",
                "transform": lambda row: (str(row["Matiere_recoupee"]).strip(),)
            },
            "CRI": {
                "table": "cri",
                "columns": ["cri"],
                "unique": "(cri)",
                "transform": lambda row: (str(row["CRI"]).strip(),)
            },
            "CENTRE": {
                "table": "centre",
                "columns": ["centre"],
                "unique": "(centre)",
                "transform": lambda row: (str(row["CENTRE"]).strip(),)
            },
            "UG": {
                "table": "ug",
                "columns": ["centre", "cri", "cdif", "crif", "cdia", "cria", "acdi", "acri", "ville", "directeur", "regional"],
                "unique": "(centre)",
                "transform": lambda row: (
                    str(row["CENTRE"]).strip(),
                    str(row["CRI"]).strip(),
                    str(row["CDIF"]).strip(),
                    str(row["CRIF"]).strip(),
                    str(row["CDIA"]).strip(),
                    str(row["CRIA"]).strip(),
                    str(row["ACDI"]).strip(),
                    str(row["ACRI"]).strip(),
                    str(row["VILLE"]).strip(),
                    str(row["DIRECTEUR"]).strip(),
                    str(row["REGIONAL"]).strip()
                )
            },
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
                chunk_size=1000
            )
            conn.commit()  # commit après chaque table

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