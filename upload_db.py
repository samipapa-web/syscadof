# ========================================
# MIGRATION ULTRA RAPIDE POSTGRES → POSTGRES (COPY)
# VERSION ROBUSTE + SECURISEE
# ========================================

import psycopg2
import os
import io

# =========================================================
# CONFIGURATION BASE SOURCE (LOCALE)
# =========================================================
DB_SOURCE_CONFIG = {
    "host": "127.0.0.1",  # ✅ IMPORTANT (évite erreur IPv6)
    "port": 5432,
    "dbname": "syscadof",
    "user": "postgres",
    "password": "samipapa"
}

# =========================================================
# CONFIGURATION BASE CIBLE (ENVIRONNEMENT)
# =========================================================
DB_TARGET_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

# =========================================================
# INITIALISATION PASSWORD (OPTIONNEL - DEV UNIQUEMENT)
# =========================================================
def set_postgres_password():
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            port=5432,
            dbname="postgres",
            user="postgres",
            password="samipapa"
        )
        cur = conn.cursor()

        cur.execute("ALTER USER postgres WITH PASSWORD %s;", ("samipapa",))
        conn.commit()

        print("🔐 Mot de passe postgres défini")

    except Exception as e:
        print(f"⚠️ Impossible de définir le mot de passe : {e}")

    finally:
        if 'conn' in locals():
            conn.close()

# =========================================================
# CONNEXIONS
# =========================================================
def get_source_connection():
    try:
        conn = psycopg2.connect(**DB_SOURCE_CONFIG)
        print("✅ Connexion SOURCE OK")
        return conn
    except Exception as e:
        print(f"❌ Connexion SOURCE échouée : {e}")
        raise


def get_target_connection():
    try:
        conn = psycopg2.connect(**DB_TARGET_CONFIG)
        print("✅ Connexion CIBLE OK")
        return conn
    except Exception as e:
        print(f"❌ Connexion CIBLE échouée : {e}")
        raise

# =========================================================
# TRUNCATE TABLE
# =========================================================
def truncate_table(conn, table_name):
    cur = conn.cursor()
    try:
        cur.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
        conn.commit()
        print(f"🧹 Table vidée : {table_name}")
    except Exception as e:
        print(f"❌ Erreur TRUNCATE {table_name} : {e}")
        conn.rollback()
    finally:
        cur.close()

# =========================================================
# COPY ULTRA RAPIDE
# =========================================================
def copy_table_fast(source_conn, target_conn, table_name, columns):
    src_cur = source_conn.cursor()
    tgt_cur = target_conn.cursor()

    try:
        print(f"⏳ Lecture : {table_name}")

        src_cur.execute(f"SELECT {', '.join(columns)} FROM {table_name}")

        buffer = io.StringIO()

        for row in src_cur:
            line = "\t".join(
                "" if v is None else str(v).replace("\t", " ").replace("\n", " ")
                for v in row
            )
            buffer.write(line + "\n")

        buffer.seek(0)

        print(f"🚀 COPY : {table_name}")

        copy_sql = f"""
            COPY {table_name} ({', '.join(columns)})
            FROM STDIN WITH (FORMAT text)
        """

        tgt_cur.copy_expert(copy_sql, buffer)

        print(f"✅ Copie réussie : {table_name}")

    except Exception as e:
        print(f"❌ Erreur COPY {table_name} : {e}")
        target_conn.rollback()

    finally:
        src_cur.close()
        tgt_cur.close()

# =========================================================
# TABLES (ORDRE IMPORTANT)
# =========================================================
TABLES_CONFIG = [
    ("roles", ["role_name", "permissions"]),
    ("users", ["username", "password", "role_name"]),
    ("risques", ["chapitre", "risque", "axe"]),
    ("notifs", ["type_notification", "modele_notification"]),
    ("matieres", ["matiere_recoupee"]),
    ("cri", ["cri"]),
    ("centre", ["centre"]),
    ("ug", ["centre", "cri", "cdif", "crif", "cdia", "cria", "acdi", "acri", "ville", "directeur", "regional"]),
    ("niu", ["niu", "raison_sociale", "sigle", "activite", "regime", "centre", "etat", "telephone"]),
    ("sources_donnees", ["intitule_source", "provenance", "fournisseur", "categorie", "temporalite"])
]

# =========================================================
# MIGRATION GLOBALE
# =========================================================
def migrate_database_fast():
    try:
        print("🔌 Connexion aux bases...")

        source_conn = get_source_connection()
        target_conn = get_target_connection()

        print("\n🚀 Début migration...")

        for table_name, columns in TABLES_CONFIG:
            print("\n==============================")
            print(f"📦 Table : {table_name}")

            truncate_table(target_conn, table_name)

            copy_table_fast(
                source_conn,
                target_conn,
                table_name,
                columns
            )

            target_conn.commit()

        source_conn.close()
        target_conn.close()

        print("\n🎯 MIGRATION TERMINÉE AVEC SUCCÈS")

    except Exception as e:
        print(f"\n❌ ERREUR GLOBALE : {e}")

# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":
    print("=======================================")
    print(" MIGRATION POSTGRES ULTRA RAPIDE (COPY)")
    print("=======================================")

    # ⚠️ À utiliser UNE SEULE FOIS si besoin
    #set_postgres_password()

    migrate_database_fast()