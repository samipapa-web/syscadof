# Modules/valorisation/services.py
#--------------------------------------------------------

import os
from datetime import datetime
from werkzeug.utils import secure_filename
from psycopg2.extras import RealDictCursor
from flask import current_app

from database import get_connection
from .scripts.script_valorisation import traitement_valorisation


# ===============================
# INIT TABLE
# ===============================
def init_valorisation_table():
    conn = get_connection()
    cur = conn.cursor()

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
    cur.close()
    conn.close()


# ===============================
# SELECTS
# ===============================
def get_recent_exploiter_files():
    sortie_dir = current_app.config["SORTIE_DIR"]
    files = [f for f in os.listdir(sortie_dir)
             if f.lower().startswith("exploiter") and f.endswith(".xlsx")]
    files.sort(reverse=True)
    return files[:20]


# -------------------------------
# MATIERES (DB)
# -------------------------------
def get_matieres():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT matiere_recoupee
            FROM matieres
            WHERE matiere_recoupee IS NOT NULL
            ORDER BY matiere_recoupee
        """)
        return [row["matiere_recoupee"] for row in cur.fetchall()]

    finally:
        cur.close()
        conn.close()


# -------------------------------
# CHAPITRES (DB)
# -------------------------------
def get_chapitres():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT DISTINCT chapitre
            FROM risques
            WHERE chapitre IS NOT NULL
            ORDER BY chapitre
        """)
        return [row["chapitre"] for row in cur.fetchall()]

    finally:
        cur.close()
        conn.close()


# -------------------------------
# RISQUES PAR CHAPITRE (DB)
# -------------------------------
def get_risques_by_chapitre(chapitre):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT DISTINCT risque
            FROM risques
            WHERE TRIM(LOWER(chapitre)) = TRIM(LOWER(%s))
            ORDER BY risque
        """, (chapitre,))
        return [row["risque"] for row in cur.fetchall()]

    finally:
        cur.close()
        conn.close()


# -------------------------------
# AXES (DB)
# -------------------------------
def get_axes(chapitre, risque):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT axe
            FROM risques
            WHERE TRIM(LOWER(chapitre)) = TRIM(LOWER(%s))
              AND TRIM(LOWER(risque)) = TRIM(LOWER(%s))
            ORDER BY axe
        """, (chapitre, risque))

        return [row["axe"] for row in cur.fetchall()]

    finally:
        cur.close()
        conn.close()


# ===============================
# SCRIPTS
# ===============================
def list_scripts():
    script_dir = current_app.config["VALO_SCRIPT_DIR"]
    return [f for f in os.listdir(script_dir) if f.endswith(".py")]


def load_script_content(name):
    script_dir = current_app.config["VALO_SCRIPT_DIR"]
    path = os.path.join(script_dir, secure_filename(name))

    if not os.path.exists(path):
        return ""

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_script_file(name, content):
    script_dir = current_app.config["VALO_SCRIPT_DIR"]

    filename = secure_filename(name)
    if not filename.endswith(".py"):
        filename += ".py"

    path = os.path.join(script_dir, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return {"success": True, "message": "Script sauvegardé avec succès."}


# ===============================
# EXECUTION
# ===============================
def execute_valorisation_process(
    fichier, matiere, chapitre, risque, axe,
    script, impots_inclus, autre_taxe, utilisateur="system"
):
    try:
        fichier = secure_filename(fichier)
        historique_id = int(datetime.now().timestamp())

        result = traitement_valorisation(
            fichier=fichier,
            matiere=matiere,
            risque=risque,
            axe=axe,
            historique_id=historique_id,
            impots_inclus=impots_inclus,
            autre_taxe=autre_taxe
        )

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO valorisation (
                nom_fichier, chapitre, risque, axe,
                script_utilise, utilisateur, impots_inclus, date_generation
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            result["fichier_genere"],
            chapitre,
            risque,
            axe,
            script,
            utilisateur,
            ", ".join(impots_inclus),
            datetime.now()
        ))

        conn.commit()
        cur.close()
        conn.close()

        return {"success": True, "message": result["message"]}

    except Exception as e:
        return {"success": False, "message": str(e)}


# ===============================
# HISTORIQUE
# ===============================
def get_historique():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM valorisation ORDER BY id DESC")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows