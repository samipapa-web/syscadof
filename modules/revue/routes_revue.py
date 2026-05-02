# modules/revue/routes_revue.py
# ---------------------------------------

from flask import Blueprint, render_template, jsonify, request, current_app, send_from_directory
import os
from contextlib import contextmanager
from werkzeug.utils import secure_filename

from database import get_connection, release_connection
from .services_revue import get_filtres_data
from .scripts.script_revue import run_revue


revue_bp = Blueprint(
    "revue",
    __name__,
    url_prefix="/revue",
    template_folder="templates"
)

# =========================================================
# DB CONTEXT
# =========================================================
@contextmanager
def db_conn():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    finally:
        release_connection(conn)

# =========================================================
# PAGE PRINCIPALE
# =========================================================
@revue_bp.route("/")
def page():
    return render_template("revue.html")

# =========================================================
# INIT FILTRES
# =========================================================
@revue_bp.route("/api/init")
def init():
    try:
        centres, cris = get_filtres_data()
        return jsonify({
            "centres": centres,
            "cris": cris
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur init: {str(e)}"
        })

# =========================================================
# EXECUTION REVUE
# =========================================================
@revue_bp.route("/api/run", methods=["POST"])
def run():
    data = request.get_json(silent=True) or {}

    try:
        # 🔥 récupération paramètres (AVEC CLE)
        niu = (data.get("niu") or "").strip()
        cri = (data.get("cri") or "").strip()
        centre = (data.get("centre") or "").strip()
        cle = (data.get("cle") or "").strip()

        result = run_revue(
            niu=niu if niu else None,
            cri=cri if cri else None,
            centre=centre if centre else None,
            cle=cle if cle else None,
            sortie_dir=current_app.config["SORTIE_DIR"],
            template_dir=current_app.config["TEMPLATES_DIR"]
        )

        # 🔥 gestion erreurs métier
        if "message" in result and "Aucun" in result["message"]:
            return jsonify(success=False, message=result["message"])

        return jsonify(
            success=True,
            message=result.get("message"),
            excel=result.get("excel"),
            docx=result.get("docx"),
            synthese=result.get("synthese"),
            detail_par_fichier=result.get("detail_par_fichier")
        )

    except Exception as e:
        return jsonify(
            success=False,
            message=f"Erreur execution: {str(e)}"
        )

# =========================================================
# TELECHARGEMENT SECURISE
# =========================================================
@revue_bp.route("/download/<path:nom>")
def download(nom):
    try:
        # 🔥 sécurisation du nom de fichier
        nom = secure_filename(nom)

        dossier = current_app.config["SORTIE_DIR"]
        chemin = os.path.join(dossier, nom)

        if not os.path.exists(chemin):
            return jsonify(success=False, message="Fichier introuvable")

        return send_from_directory(
            dossier,
            nom,
            as_attachment=True
        )

    except Exception as e:
        return jsonify(
            success=False,
            message=f"Erreur téléchargement: {str(e)}"
        )
