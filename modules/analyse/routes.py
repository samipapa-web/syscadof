import os
import pandas as pd
import sys
from datetime import datetime
from contextlib import contextmanager

from flask import (
    render_template,
    request,
    jsonify,
    send_from_directory,
    abort,
    session,
    current_app
)

from werkzeug.utils import secure_filename
from psycopg2.extras import RealDictCursor

from .services import run_script
from . import analyse_bp

from database import get_connection, release_connection


# =========================================================
# CONTEXT MANAGER DB (CRITIQUE)
# =========================================================
@contextmanager
def db_conn():
    conn = get_connection()
    try:
        yield conn
    finally:
        release_connection(conn)


# =========================================================
# PAGE PRINCIPALE
# =========================================================
@analyse_bp.route("/")
def analyse_page():

    with db_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            # Création table si inexistante
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

            # Lecture
            cur.execute("""
                SELECT * FROM croisements
                ORDER BY date_stockage DESC
            """)

            croisements = cur.fetchall()

    return render_template("analyse.html", croisements=croisements)


# =========================================================
# SOURCES
# =========================================================
@analyse_bp.route("/api/sources-lac")
def list_sources_lac():

    try:
        with db_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:

                cur.execute("""
                    SELECT id, intitule_source, nom_fichier, annee, mois
                    FROM sources_clean
                    ORDER BY date_stockage DESC
                """)

                data = cur.fetchall()

        return jsonify(data)

    except Exception as e:
        current_app.logger.error(f"ERREUR sources-lac: {e}")
        return jsonify([]), 500


# =========================================================
# SCRIPTS
# =========================================================
@analyse_bp.route("/api/scripts")
def list_scripts():

    try:
        scripts_dir = current_app.config["ANAL_SCRIPT_DIR"]

        fichiers = [
            f for f in os.listdir(scripts_dir)
            if f.endswith(".py")
        ]

        return jsonify([
            {"id": f, "titre": f.replace(".py", "")}
            for f in fichiers
        ])

    except Exception as e:
        current_app.logger.error(f"ERREUR scripts: {e}")
        return jsonify([]), 500


# =========================================================
# CHARGER SCRIPT
# =========================================================
@analyse_bp.route("/api/get-script/<script_name>")
def get_script(script_name):

    try:
        scripts_dir = current_app.config["ANAL_SCRIPT_DIR"]

        if ".." in script_name:
            return jsonify(success=False, error="Nom invalide")

        chemin = os.path.join(scripts_dir, script_name)

        if not os.path.exists(chemin):
            return jsonify(success=False, error="Introuvable")

        with open(chemin, "r", encoding="utf-8") as f:
            contenu = f.read()

        return jsonify(success=True, contenu=contenu)

    except Exception as e:
        current_app.logger.error(f"ERREUR get-script: {e}")
        return jsonify(success=False, error=str(e)), 500


# =========================================================
# SAVE SCRIPT
# =========================================================
@analyse_bp.route("/api/save-new-script", methods=["POST"])
def save_new_script():

    try:
        data = request.get_json()

        titre = data.get("titre")
        contenu = data.get("contenu")

        if not titre or not contenu:
            return jsonify(success=False, error="Champs manquants")

        scripts_dir = current_app.config["ANAL_SCRIPT_DIR"]

        nom_fichier = titre.replace(" ", "_").lower() + ".py"
        chemin = os.path.join(scripts_dir, nom_fichier)

        if os.path.exists(chemin):
            return jsonify(success=False, error="Existe déjà")

        with open(chemin, "w", encoding="utf-8") as f:
            f.write(contenu)

        return jsonify(success=True, message="Script enregistré")

    except Exception as e:
        current_app.logger.error(f"ERREUR save-script: {e}")
        return jsonify(success=False, error=str(e)), 500


# =========================================================
# EXECUTION SCRIPT
# =========================================================
@analyse_bp.route("/api/run-script/<script_name>", methods=["POST"])
def execute(script_name):

    try:
        source_a_id = request.form.get("source_a_id")
        source_b_id = request.form.get("source_b_id")
        script_contenu = request.form.get("script_contenu")

        if not source_a_id or not source_b_id:
            return jsonify(success=False, error="Sources manquantes")

        success, data = run_script(
            script_name,
            source_a_id,
            source_b_id,
            script_contenu
        )

        if not success:
            return jsonify(success=False, error=data.get("error"))

        # (Optionnel) Log pour debug production
        current_app.logger.info(f"[ANALYSE RUN] {data}")

        return jsonify(
            success=True,
            message=data.get("message"),
            resultat_sortie=data.get("resultat_sortie"),
            utilisateur=data.get("utilisateur")
        )

    except Exception as e:
        current_app.logger.error(f"ERREUR run-script: {e}")
        return jsonify(success=False, error=str(e)), 500


# =========================================================
# TABLEUR
# =========================================================
@analyse_bp.route("/tableur_analyse/<path:filename>")
def tableur_analyse(filename):

    try:
        safe = secure_filename(filename)

        sortie_dir = current_app.config["SORTIE_DIR"]
        path = os.path.join(sortie_dir, safe)

        if not os.path.exists(path):
            abort(404)

        if safe.endswith(".csv"):
            df = pd.read_csv(path)
        elif safe.endswith(".xlsx"):
            df = pd.read_excel(path, engine="openpyxl")
        else:
            abort(400)

        return render_template(
            "tableur_analyse.html",
            data=df.to_dict(orient="records"),
            columns=df.columns.tolist(),
            filename=safe
        )

    except Exception as e:
        current_app.logger.error(f"ERREUR tableur: {e}")
        abort(500)


# =========================================================
# DOWNLOAD
# =========================================================
@analyse_bp.route("/download/<path:filename>")
def download_sortie(filename):

    try:
        safe = secure_filename(filename)
        sortie_dir = current_app.config["SORTIE_DIR"]

        return send_from_directory(sortie_dir, safe, as_attachment=True)

    except Exception as e:
        current_app.logger.error(f"ERREUR download: {e}")
        abort(500)
