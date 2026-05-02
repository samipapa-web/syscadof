# modules/traitement/routes.py
#------------------------------------------------------------------------------

from flask import Blueprint, jsonify, request, render_template, send_from_directory, abort, current_app
import os
from datetime import datetime
import pandas as pd
from werkzeug.utils import secure_filename
from contextlib import contextmanager
from psycopg2.extras import RealDictCursor

# Service script
from modules.traitement.services import execute_script

# DB
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from database import get_connection, release_connection

traitement_bp = Blueprint(
    "traitement",
    __name__,
    url_prefix="/traitement",
    template_folder="templates"
)

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


# =========================
# PAGE
# =========================
@traitement_bp.route("/editor")
def editor():
    return render_template("editor.html")


# =========================
# SOURCES LAC
# =========================
@traitement_bp.route("/api/sources-lac")
def list_sources_lac():
    try:
        with db_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, intitule_source, annee, mois, nom_fichier
                    FROM sources_lac
                    ORDER BY date_stockage DESC
                """)
                rows = cur.fetchall()

        return jsonify(rows)

    except Exception as e:
        current_app.logger.error(f"ERREUR sources-lac: {e}")
        return jsonify([]), 500


# =========================
# HISTORIQUE
# =========================
@traitement_bp.route("/api/historique-sources-apurees")
def historique_sources_apurees():
    try:
        with db_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT source_id, intitule_source, categorie, fournisseur, temporalite,
                           annee, mois, type_fichier, nom_fichier,
                           utilisateur, date_apurement, statut
                    FROM sources_clean
                    ORDER BY date_apurement DESC NULLS LAST
                """)
                rows = cur.fetchall()

        return jsonify(rows)

    except Exception as e:
        current_app.logger.error(f"ERREUR historique: {e}")
        return jsonify([]), 500


# =========================
# SCRIPTS
# =========================
@traitement_bp.route("/api/scripts")
def list_scripts():
    try:
        from psycopg2.extras import RealDictCursor

        with db_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, titre, auteur
                    FROM base_scripts
                    ORDER BY date_stockage DESC
                """)
                rows = cur.fetchall()

        return jsonify(rows)

    except Exception as e:
        current_app.logger.error(f"ERREUR scripts: {e}")
        return jsonify([]), 500


# =========================
# GET SCRIPT
# =========================
@traitement_bp.route("/api/get-script/<int:script_id>")
def get_script(script_id):
    try:
        with db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT chemin_script FROM base_scripts WHERE id=%s", (script_id,))
                row = cur.fetchone()

        if not row:
            return jsonify({"success": False, "error": "Script introuvable"})

        chemin = row[0] if isinstance(row, tuple) else row["chemin_script"]

        if not os.path.exists(chemin):
            return jsonify({"success": False, "error": "Fichier absent"})

        with open(chemin, "r", encoding="utf-8") as f:
            contenu = f.read()

        return jsonify({"success": True, "contenu": contenu})

    except Exception as e:
        current_app.logger.error(f"ERREUR get-script: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# =========================
# EXECUTION SCRIPT
# =========================
@traitement_bp.route("/api/run-script/<int:script_id>", methods=["POST"])
def run_script(script_id):
    try:
        source_lac_id = request.form.get("source_lac_id")
        if not source_lac_id:
            raise Exception("source_lac_id manquant")

        BASE_DIR = current_app.config["BASE_DIR"]

        with db_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:

                # Script
                cur.execute("SELECT chemin_script FROM base_scripts WHERE id=%s", (script_id,))
                script = cur.fetchone()
                if not script:
                    raise Exception("Script introuvable")

                chemin_script = script[0] if isinstance(script, tuple) else script["chemin_script"]

                # Source
                cur.execute("SELECT * FROM sources_lac WHERE id=%s", (source_lac_id,))
                source = cur.fetchone()
                if not source:
                    raise Exception("Source introuvable")

                # Exécution
                output = execute_script(chemin_script, source_lac_id, BASE_DIR)

                parts = output.split("||")
                if len(parts) != 2:
                    raise Exception("Format de sortie invalide")

                chemin_clean, nom_clean = parts

                # Insert
                cur.execute("""
                    INSERT INTO sources_clean (
                        source_id, intitule_source, provenance, categorie,
                        fournisseur, temporalite, annee, mois, type_fichier,
                        chemin, nom_fichier, utilisateur,
                        date_stockage, date_apurement, statut
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    source["id"],
                    source["intitule_source"],
                    source["provenance"],
                    source["categorie"],
                    source["fournisseur"],
                    source["temporalite"],
                    source["annee"],
                    source["mois"],
                    source["type_fichier"],
                    chemin_clean,
                    nom_clean,
                    source["utilisateur"],
                    source["date_stockage"],
                    datetime.now(),
                    "Succès"
                ))

                conn.commit()

        return jsonify({"success": True})

    except Exception as e:
        current_app.logger.error(f"ERREUR run-script: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# =========================
# SAVE SCRIPT
# =========================
@traitement_bp.route("/api/save-script", methods=["POST"])
def save_script():
    try:
        titre = request.form.get("titre")
        contenu = request.form.get("contenu")

        if not titre or not contenu:
            raise Exception("Titre ou contenu manquant")

        # ⚡ dossier des scripts
        SCRIPTS_DIR = current_app.config["APUR_SCRIPT_DIR"]

        os.makedirs(SCRIPTS_DIR, exist_ok=True)

        # sécuriser le nom
        filename = secure_filename(titre) + ".py"
        chemin_script = os.path.join(SCRIPTS_DIR, filename)

        # éviter écrasement (optionnel mais conseillé)
        if os.path.exists(chemin_script):
            raise Exception("Un script avec ce nom existe déjà")

        # écrire le fichier
        with open(chemin_script, "w", encoding="utf-8") as f:
            f.write(contenu)

        # insertion en base
        with db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO base_scripts (titre, object, auteur, chemin_script, date_stockage)
                    VALUES (%s, %s, %s, %s, NOW())
                """, (
                    titre,
                    "Traitement",
                    ".",
                    chemin_script
                ))
                conn.commit()

        return jsonify({"success": True})

    except Exception as e:
        current_app.logger.error(f"ERREUR save-script: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# =========================
# TABLEUR
# =========================
@traitement_bp.route("/tableur/<filename>")
def view_tableur(filename):
    try:
        CLEAN_DIR = current_app.config["DATA_CLEAN_DIR"]
        safe = secure_filename(filename)
        file_path = os.path.join(CLEAN_DIR, safe)

        if not os.path.exists(file_path):
            abort(404)

        df = pd.read_csv(file_path, nrows=1) if filename.endswith(".csv") else pd.read_excel(file_path, nrows=1)

        return render_template("tableur.html", filename=filename, columns=df.columns)

    except Exception as e:
        current_app.logger.error(f"ERREUR tableur: {e}")
        abort(500)


# =========================
# DATA TABLEUR
# =========================
@traitement_bp.route("/api/tableur-data/<filename>")
def tableur_data(filename):
    try:
        CLEAN_DIR = current_app.config["DATA_CLEAN_DIR"]
        safe = secure_filename(filename)
        file_path = os.path.join(CLEAN_DIR, safe)

        if not os.path.exists(file_path):
            return jsonify({"data": []})

        df = pd.read_csv(file_path, dtype=str) if filename.endswith(".csv") else pd.read_excel(file_path, dtype=str)

        return jsonify({
            "draw": 1,
            "recordsTotal": len(df),
            "recordsFiltered": len(df),
            "data": df.fillna("").to_dict(orient="records")
        })

    except Exception as e:
        current_app.logger.error(f"ERREUR tableur-data: {e}")
        return jsonify({"data": []}), 500


# =========================
# DOWNLOAD
# =========================
@traitement_bp.route("/download/<path:filename>")
def download_sortie(filename):
    try:
        CLEAN_DIR = current_app.config["DATA_CLEAN_DIR"]
        safe = secure_filename(filename)
        return send_from_directory(CLEAN_DIR, safe, as_attachment=True)

    except Exception as e:
        current_app.logger.error(f"ERREUR download: {e}")
        abort(500)
