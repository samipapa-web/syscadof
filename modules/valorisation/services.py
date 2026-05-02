# modules/valorisation/services.py
# ----------------------------------------------------------

import os
import uuid
import traceback
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename

from database import get_connection, release_connection, get_cursor
from .scripts.script_valorisation import traitement_valorisation


# =========================================================
# DOSSIER SORTIE SECURISE
# =========================================================
def safe_output_dir():
    path = current_app.config.get("SORTIE_DIR", "/tmp/sortie")
    os.makedirs(path, exist_ok=True)
    return path


# =========================================================
# INIT TABLE
# =========================================================
def init_valorisation_table():
    conn = get_connection()
    try:
        cur = get_cursor(conn)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS valorisation (
                id SERIAL PRIMARY KEY,
                nom_fichier TEXT,
                chapitre TEXT,
                risque TEXT,
                axe TEXT,
                script_utilise TEXT,
                utilisateur TEXT,
                impots_inclus TEXT,
                date_generation TIMESTAMP
            )
        """)

        conn.commit()

    finally:
        if cur:
            cur.close()
        release_connection(conn)


# =========================================================
# LISTE DES FICHIERS EXPLOITER
# =========================================================
def get_recent_exploiter_files():
    path = safe_output_dir()

    files = [
        f for f in os.listdir(path)
        if f.lower().startswith("exploiter") and f.lower().endswith(".xlsx")
    ]

    files.sort(reverse=True)
    return files[:20]


# =========================================================
# MATIERES
# =========================================================
def get_matieres():
    conn = get_connection()
    try:
        cur = get_cursor(conn)

        cur.execute("""
            SELECT matiere_recoupee
            FROM matieres
            WHERE matiere_recoupee IS NOT NULL
            ORDER BY matiere_recoupee
        """)

        return [r["matiere_recoupee"] for r in cur.fetchall()]

    finally:
        if cur:
            cur.close()
        release_connection(conn)


# =========================================================
# CHAPITRES
# =========================================================
def get_chapitres():
    conn = get_connection()
    try:
        cur = get_cursor(conn)

        cur.execute("""
            SELECT DISTINCT chapitre
            FROM risques
            WHERE chapitre IS NOT NULL
            ORDER BY chapitre
        """)

        return [r["chapitre"] for r in cur.fetchall()]

    finally:
        if cur:
            cur.close()
        release_connection(conn)


# =========================================================
# RISQUES
# =========================================================
def get_risques_by_chapitre(chapitre):
    if not chapitre:
        return []

    conn = get_connection()
    try:
        cur = get_cursor(conn)

        cur.execute("""
            SELECT DISTINCT risque
            FROM risques
            WHERE LOWER(chapitre) = LOWER(%s)
            ORDER BY risque
        """, (chapitre,))

        return [r["risque"] for r in cur.fetchall()]

    finally:
        if cur:
            cur.close()
        release_connection(conn)


# =========================================================
# AXES
# =========================================================
def get_axes(chapitre, risque):
    if not chapitre or not risque:
        return []

    conn = get_connection()
    try:
        cur = get_cursor(conn)

        cur.execute("""
            SELECT axe
            FROM risques
            WHERE LOWER(chapitre) = LOWER(%s)
              AND LOWER(risque) = LOWER(%s)
            ORDER BY axe
        """, (chapitre, risque))

        return [r["axe"] for r in cur.fetchall()]

    finally:
        if cur:
            cur.close()
        release_connection(conn)


# =========================================================
# SCRIPTS
# =========================================================
def list_scripts():
    path = current_app.config.get("VALO_SCRIPT_DIR", "modules/valorisation/scripts")
    os.makedirs(path, exist_ok=True)

    return [f for f in os.listdir(path) if f.endswith(".py")]


def load_script_content(name):
    path = os.path.join(
        current_app.config.get("VALO_SCRIPT_DIR", "modules/valorisation/scripts"),
        secure_filename(name)
    )

    if not os.path.exists(path):
        return ""

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_script_file(name, content):
    path_dir = current_app.config.get("VALO_SCRIPT_DIR", "modules/valorisation/scripts")
    os.makedirs(path_dir, exist_ok=True)

    filename = secure_filename(name)
    if not filename.endswith(".py"):
        filename += ".py"

    path = os.path.join(path_dir, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return {"success": True, "message": "Script sauvegardé"}


# =========================================================
# EXECUTION PRINCIPALE (CORRIGÉE)
# =========================================================
def execute_valorisation_process(
    fichier,
    matiere,
    chapitre,
    risque,
    axe,
    script,
    impots_inclus,
    autre_taxe,
    utilisateur="system"
):
    conn = None
    cur = None

    try:
        fichier = secure_filename(fichier)
        historique_id = uuid.uuid4().int >> 64

        # ===============================
        # EXECUTION METIER
        # ===============================
        result = traitement_valorisation(
            fichier=fichier,
            matiere=matiere,
            risque=risque,
            axe=axe,
            historique_id=historique_id,
            impots_inclus=impots_inclus,
            autre_taxe=autre_taxe
        )

        if not result.get("fichier_genere"):
            raise ValueError(result.get("message"))

        # ===============================
        # INSERT DB
        # ===============================
        conn = get_connection()
        cur = get_cursor(conn)

        cur.execute("""
            INSERT INTO valorisation (
                nom_fichier, chapitre, risque, axe,
                script_utilise, utilisateur,
                impots_inclus, date_generation
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            result["fichier_genere"],
            chapitre,
            risque,
            axe,
            script,
            utilisateur,
            ", ".join(impots_inclus or []),
            datetime.now()
        ))

        conn.commit()

        return {
            "success": True,
            "message": result["message"],
            "fichier": result["fichier_genere"]
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "trace": traceback.format_exc()
        }

    finally:
        if cur:
            cur.close()
        if conn:
            release_connection(conn)


# =========================================================
# HISTORIQUE
# =========================================================
def get_historique():
    conn = get_connection()
    try:
        cur = get_cursor(conn)

        cur.execute("""
            SELECT *
            FROM valorisation
            ORDER BY id DESC
        """)

        return cur.fetchall()

    finally:
        if cur:
            cur.close()
        release_connection(conn)
