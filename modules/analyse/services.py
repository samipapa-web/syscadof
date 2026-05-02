# modules/analyse/services.py
# ----------------------------------------------------------

import os
from datetime import datetime
from flask import current_app, session
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

from database import get_connection, release_connection


# =========================================================
# CONTEXT MANAGER DB (COMME TRAITEMENT)
# =========================================================
@contextmanager
def db_conn():
    conn = get_connection()
    try:
        yield conn
    finally:
        release_connection(conn)


# =========================================================
# EXÉCUTION SCRIPT ANALYSE
# =========================================================
def run_script(script_id, source_a_id, source_b_id, script_code=None):

    if not script_code:
        return False, {"error": "Script vide"}

    sortie_dir = current_app.config["SORTIE_DIR"]
    clean_dir = current_app.config.get("DATA_CLEAN_DIR")

    utilisateur = session.get("user", "system")

    # 🔥 ENV D’EXECUTION PROPRE
    exec_env = {
        "source_a_id": int(source_a_id),
        "source_b_id": int(source_b_id),
        "SORTIE_DIR": sortie_dir,
        "CLEAN_DIR": clean_dir,
        "session": session,
        "db_conn": db_conn,  # ✅ NOUVEAU (important)
        "__builtins__": __builtins__,
    }

    try:
        exec(script_code, exec_env)

        dernier = exec_env.get("dernier_croisement")

        if not dernier:
            return False, {"error": "Le script doit définir 'dernier_croisement'"}

        nom_fichier = dernier.get("nom_fichier")
        type_fichier = dernier.get("type_fichier", "xlsx")

        if not nom_fichier:
            return False, {"error": "nom_fichier manquant"}

        # =========================================================
        # INSERT PROPRE AVEC RealDictCursor
        # =========================================================
        with db_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS croisements (
                        id SERIAL PRIMARY KEY,
                        id_source_a INTEGER,
                        id_source_b INTEGER,
                        nom_fichier TEXT,
                        type_fichier TEXT,
                        utilisateur TEXT,
                        date_stockage TIMESTAMP
                    )
                """)

                cur.execute("""
                    INSERT INTO croisements
                    (id_source_a, id_source_b, nom_fichier, type_fichier, utilisateur, date_stockage)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    dernier.get("id_source_a"),
                    dernier.get("id_source_b"),
                    nom_fichier,
                    type_fichier,
                    dernier.get("utilisateur", utilisateur),
                    datetime.now()
                ))

                conn.commit()

        return True, {
            "message": f"Fichier généré : {nom_fichier}",
            "resultat_sortie": nom_fichier,
            "utilisateur": dernier.get("utilisateur", utilisateur)
        }

    except Exception as e:
        return False, {"error": f"Erreur exécution script : {str(e)}"}
