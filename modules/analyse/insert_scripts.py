# modules/analyse/insert_scripts.py
# -----------------------------------------------

import os
from datetime import datetime
from flask import current_app

# Connexion centralisée (IMPORTANT)
from modules.traitement.routes import get_pg_connection


# ===============================
# LISTE DES SCRIPTS
# ===============================
def list_scripts(app=None):
    """Lister tous les scripts présents dans le dossier"""

    cfg = app.config if app else current_app.config
    SCRIPTS_FOLDER = cfg.get("ANAL_SCRIPT_DIR")

    scripts = []

    if os.path.exists(SCRIPTS_FOLDER):
        for f in os.listdir(SCRIPTS_FOLDER):
            if f.endswith(".py"):
                scripts.append({
                    "id": f,
                    "titre": os.path.splitext(f)[0],
                    "auteur": "Admin"
                })

    return scripts


# ===============================
# CHARGEMENT D’UN SCRIPT
# ===============================
def load_script(script_name, app=None):
    """Charger le contenu d’un script"""

    cfg = app.config if app else current_app.config
    SCRIPTS_FOLDER = cfg.get("ANAL_SCRIPT_DIR")

    # Sécurité
    if ".." in script_name or "/" in script_name or "\\" in script_name:
        return "", False, "Nom de script invalide"

    script_path = os.path.join(SCRIPTS_FOLDER, script_name)

    if not os.path.exists(script_path):
        return "", False, "Script introuvable"

    try:
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        return content, True, None

    except Exception as e:
        return "", False, str(e)


# ===============================
# SAUVEGARDE + INSERTION BDD
# ===============================
def save_script(titre, contenu, auteur="Admin", object_type="Analyse", app=None):
    """Sauvegarder un script et l’insérer en base PostgreSQL"""

    cfg = app.config if app else current_app.config
    SCRIPTS_FOLDER = cfg.get("ANAL_SCRIPT_DIR")

    if not os.path.exists(SCRIPTS_FOLDER):
        os.makedirs(SCRIPTS_FOLDER)

    # Nom fichier sécurisé
    filename = titre.strip().replace(" ", "_").lower() + ".py"
    path = os.path.join(SCRIPTS_FOLDER, filename)

    if os.path.exists(path):
        return False, "", "Script déjà existant"

    conn = None
    cur = None

    try:
        # 1️⃣ Sauvegarde fichier
        with open(path, "w", encoding="utf-8") as f:
            f.write(contenu)

        # 2️⃣ Connexion PostgreSQL centralisée
        conn = get_pg_connection()
        cur = conn.cursor()

        # 3️⃣ Insertion
        cur.execute("""
            INSERT INTO base_scripts (titre, object, auteur, chemin_script, date_stockage)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (titre) DO NOTHING
        """, (
            titre,
            object_type,
            auteur,
            path,
            datetime.now()
        ))

        conn.commit()

        return True, f"Script sauvegardé : {filename}", None

    except Exception as e:
        if conn:
            conn.rollback()
        return False, "", str(e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()