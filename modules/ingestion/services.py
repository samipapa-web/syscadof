# modules/ingestion/services.py

import os
import datetime
from werkzeug.utils import secure_filename
from contextlib import contextmanager

from config import DATA_LAC_DIR, ALLOWED_EXTENSIONS

# import centralisé pour la connexion PostgreSQL
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from database import get_connection, release_connection


# =========================================================
# CONTEXT MANAGER DB (ANTI-FUITE)
# =========================================================
@contextmanager
def db_conn():
    conn = get_connection()
    try:
        yield conn
    finally:
        release_connection(conn)


# =========================================================
# VERIFICATION EXTENSION
# =========================================================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# =========================================================
# SAUVEGARDE FICHIER + DB
# =========================================================
def save_file(file, source_id, annee, mois, stockeur):
    try:
        # -----------------------------
        # VALIDATION
        # -----------------------------
        if not file or not allowed_file(file.filename):
            return {"success": False, "message": "Fichier non autorisé"}

        if not source_id or not annee:
            return {"success": False, "message": "Paramètres invalides"}

        mois = mois or 0

        # -----------------------------
        # PREPARATION FICHIER
        # -----------------------------
        ext = file.filename.rsplit(".", 1)[1].lower()

        fname = secure_filename(
            f"{source_id}_{annee}_{mois}_{int(datetime.datetime.now().timestamp())}.{ext}"
        )

        os.makedirs(DATA_LAC_DIR, exist_ok=True)
        path = os.path.join(DATA_LAC_DIR, fname)

        # -----------------------------
        # SAUVEGARDE DISQUE
        # -----------------------------
        file.save(path)

        taille = os.path.getsize(path)
        date_stockage = datetime.datetime.now()

        # -----------------------------
        # INSERTION BASE
        # -----------------------------
        with db_conn() as conn:
            with conn.cursor() as cur:

                cur.execute("""
                    INSERT INTO fichiers
                    (source_id, annee, mois, type_fichier, date_stockage, stockeur, chemin, taille)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    RETURNING id
                """, (
                    source_id,
                    annee,
                    mois,
                    ext,
                    date_stockage,
                    stockeur,
                    path,
                    taille
                ))

                fichier_id = cur.fetchone()[0]

                conn.commit()

        return {
            "success": True,
            "message": "Fichier enregistré avec succès",
            "id": fichier_id,
            "filename": fname,
            "path": path,
            "size": taille
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }
