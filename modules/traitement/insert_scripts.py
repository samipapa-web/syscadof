# modules/traitement/insert_scripts.py

import os
from datetime import datetime
from contextlib import contextmanager
from flask import current_app

# DB
import sys
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(BASE_PATH)

from database import get_connection, release_connection


# =========================================================
# CONTEXT MANAGER DB (OBLIGATOIRE)
# =========================================================
@contextmanager
def db_conn():
    conn = get_connection()
    try:
        yield conn
    finally:
        release_connection(conn)


# =========================================================
# SYNCHRONISATION
# =========================================================
def sync_scripts_to_db(app=None):
    """
    Réinitialise et insère tous les scripts Python du dossier SCRIPTS_FOLDER
    dans la table base_scripts.
    """

    # ===============================
    # CONFIG
    # ===============================
    cfg = app.config if app else current_app.config

    SCRIPTS_FOLDER = cfg.get("APUR_SCRIPT_DIR")

    if not SCRIPTS_FOLDER or not os.path.exists(SCRIPTS_FOLDER):
        raise FileNotFoundError(f"Dossier scripts introuvable : {SCRIPTS_FOLDER}")

    now = datetime.now()

    try:
        with db_conn() as conn:
            with conn.cursor() as cur:

                # 1️⃣ RESET TABLE
                cur.execute("DELETE FROM base_scripts")

                # Reset séquence (important)
                cur.execute("ALTER SEQUENCE base_scripts_id_seq RESTART WITH 1")

                # 2️⃣ INSERT SCRIPTS
                script_files = [
                    f for f in os.listdir(SCRIPTS_FOLDER)
                    if f.endswith(".py")
                ]

                for f in script_files:
                    chemin_script = os.path.join(SCRIPTS_FOLDER, f)
                    titre = os.path.splitext(f)[0]

                    cur.execute("""
                        INSERT INTO base_scripts
                        (titre, object, auteur, chemin_script, date_stockage)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        titre,
                        "Traitement",
                        ".",
                        chemin_script,
                        now
                    ))

                # 3️⃣ COMMIT UNIQUE
                conn.commit()

        print(f"[SYNC] {len(script_files)} script(s) réinitialisé(s)")

    except Exception as e:
        print(f"[SYNC ERROR] {e}")
        raise
