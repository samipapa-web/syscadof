from flask import render_template, request, jsonify, session, abort, current_app
import os
import pandas as pd
from werkzeug.utils import secure_filename

from . import valorisation_bp
from .services import (
    get_recent_exploiter_files,
    get_matieres,
    get_chapitres,
    get_risques_by_chapitre,
    get_axes,
    list_scripts,
    load_script_content,
    save_script_file,
    execute_valorisation_process,
    get_historique
)

# =========================================================
# PAGE PRINCIPALE
# =========================================================
@valorisation_bp.route("/")
def valorisation():
    return render_template("valorisation.html")


# =========================================================
# INITIALISATION
# =========================================================
@valorisation_bp.route("/api/init")
def api_init():
    try:
        return jsonify({
            "success": True,
            "fichiers": get_recent_exploiter_files(),
            "matieres": get_matieres(),
            "chapitres": get_chapitres(),
            "scripts": list_scripts()
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# =========================================================
# RISQUES
# =========================================================
@valorisation_bp.route("/api/risques")
def api_risques():
    try:
        chapitre = request.args.get("chapitre")
        return jsonify(get_risques_by_chapitre(chapitre))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================================
# AXES
# =========================================================
@valorisation_bp.route("/api/axes")
def api_axes():
    try:
        chapitre = request.args.get("chapitre")
        risque = request.args.get("risque")
        return jsonify(get_axes(chapitre, risque))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================================
# SCRIPTS
# =========================================================
@valorisation_bp.route("/api/load-script")
def api_load_script():
    try:
        name = request.args.get("name")
        if not name:
            return jsonify({"success": False, "message": "Nom script requis"}), 400

        return jsonify({
            "success": True,
            "content": load_script_content(name)
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@valorisation_bp.route("/api/save-script", methods=["POST"])
def api_save_script():
    try:
        data = request.get_json()

        if not data or "name" not in data or "content" not in data:
            return jsonify({"success": False, "message": "Données invalides"}), 400

        return jsonify(save_script_file(data["name"], data["content"]))

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# =========================================================
# EXECUTION PRINCIPALE
# =========================================================
@valorisation_bp.route("/api/execute", methods=["POST"])
def api_execute():
    try:
        data = request.get_json(force=True)

        if not data:
            return jsonify({"success": False, "message": "Requête vide"}), 400

        result = execute_valorisation_process(
            fichier=data.get("fichier"),
            matiere=data.get("matiere"),
            chapitre=data.get("chapitre"),
            risque=data.get("risque"),
            axe=data.get("axe"),
            script=data.get("script"),
            impots_inclus=data.get("impots", []),
            autre_taxe=data.get("autre_taxe", ""),
            utilisateur=session.get("user", "system")
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# =========================================================
# HISTORIQUE
# =========================================================
@valorisation_bp.route("/api/historique")
def api_historique():
    try:
        return jsonify(get_historique())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================================
# VISUALISATION TABLEUR
# =========================================================
@valorisation_bp.route("/tableur_analyse/<path:filename>")
def tableur_analyse(filename):

    safe_filename = secure_filename(filename)
    sortie_dir = current_app.config.get("SORTIE_DIR")

    if not sortie_dir:
        abort(500, description="SORTIE_DIR non configuré")

    file_path = os.path.join(sortie_dir, safe_filename)

    if not os.path.exists(file_path):
        abort(404, description=f"Fichier {safe_filename} introuvable")

    try:
        if safe_filename.lower().endswith(".csv"):
            df = pd.read_csv(file_path)

        elif safe_filename.lower().endswith(".xlsx"):
            df = pd.read_excel(file_path, engine="openpyxl")

        else:
            abort(400, description="Format non supporté")

    except Exception as e:
        abort(500, description=str(e))

    return render_template(
        "tableur_analyse.html",
        data=df.to_dict(orient="records"),
        columns=df.columns.tolist(),
        filename=safe_filename
    )
