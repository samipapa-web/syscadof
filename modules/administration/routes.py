import os
from flask import Blueprint, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from .services import list_templates, list_fichiers, save_template, save_fichier

# Blueprint pour le module ADMINISTRATION
administration_bp = Blueprint(
    "administration_bp",
    __name__,
    url_prefix="/administration",
    template_folder="templates"
)

# ==========================
# API : Liste des fichiers de Templates
# ==========================
@administration_bp.route("/api/templates")
def api_list_templates():
    """Retourne la liste des fichiers dans data/Templates"""
    try:
        files = list_templates()
        return jsonify(files)
    except Exception as e:
        return jsonify([]), 500

# ==========================
# API : Liste des fichiers de Fichiers
# ==========================
@administration_bp.route("/api/fichiers")
def api_list_fichiers():
    """Retourne la liste des fichiers dans data/Fichier"""
    try:
        files = list_fichiers()
        return jsonify(files)
    except Exception as e:
        return jsonify([]), 500

# ==========================
# Télécharger un Template
# ==========================
@administration_bp.route("/download/template/<filename>")
def download_template(filename):
    """Télécharge le fichier sélectionné du dossier Templates"""
    filename = secure_filename(filename)
    try:
        return send_from_directory(list_templates.directory, filename, as_attachment=True)
    except FileNotFoundError:
        return "Fichier non trouvé", 404

# ==========================
# Télécharger un Fichier
# ==========================
@administration_bp.route("/download/fichier/<filename>")
def download_fichier(filename):
    """Télécharge le fichier sélectionné du dossier Fichier"""
    filename = secure_filename(filename)
    try:
        return send_from_directory(list_fichiers.directory, filename, as_attachment=True)
    except FileNotFoundError:
        return "Fichier non trouvé", 404

# ==========================
# Mettre à jour un Template
# ==========================
@administration_bp.route("/update/template/<filename>", methods=["POST"])
def update_template(filename):
    """Remplace le fichier Template existant par un nouveau fichier uploadé"""
    file = request.files.get("file")
    if not file:
        return jsonify(success=False, message="Aucun fichier sélectionné")
    try:
        result = save_template(filename, file)
        return jsonify(result)
    except Exception as e:
        return jsonify(success=False, message=str(e))

# ==========================
# Mettre à jour un Fichier
# ==========================
@administration_bp.route("/update/fichier/<filename>", methods=["POST"])
def update_fichier(filename):
    """Remplace le fichier Fichier existant par un nouveau fichier uploadé"""
    file = request.files.get("file")
    if not file:
        return jsonify(success=False, message="Aucun fichier sélectionné")
    try:
        result = save_fichier(filename, file)
        return jsonify(result)
    except Exception as e:
        return jsonify(success=False, message=str(e))

# ==========================
# Page principale du module ADMINISTRATION
# ==========================
@administration_bp.route("/")
def administration_page():
    """Affiche la page HTML du module administration avec bannière et sidebar"""
    from flask import render_template

    # ⚡ Modules injectés depuis app.py via context_processor
    return render_template("administration.html")