#
# modules\admistration\templates\administration.html
#
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>ADMINISTRATION</title>

<!-- ============================
     Styles généraux + sidebar
============================= -->
<style>
html, body { margin:0; padding:0; font-family: Arial,sans-serif; background: #f3f4f6; }

/* Bannière fixée en haut */
.banniere-container { position: fixed; top:0; left:0; width:100%; z-index:1000; }
.banniere-container img { width:100%; height:auto; display:block; }

/* Variables dynamiques */
:root { --banner-height:0px; }

/* Sidebar fixe */
.sidebar {
    position: fixed;
    top: var(--banner-height);
    left:0; bottom:0;
    width:110px;
    background-color: #1e293b;
    overflow-y: auto;
    padding-top:10px;
}
.sidebar a {
    display:block;
    margin:10px;
    padding:10px 5px;
    text-align:center;
    color:white;
    text-decoration:none;
    font-weight:bold;
    border-radius:4px;
    background-color: #127291;
    font-size:12px;
}
.sidebar a:hover { background-color:#0d5a72; }

/* Contenu principal */
.main-content {
    margin-left:110px;
    padding:20px;
    padding-top: calc(20px + var(--banner-height));
    overflow-x:auto;
}

/* Formulaire & boutons */
select, button, input { padding:8px; margin-top:10px; width:100%; }
button { background:#2099b6; color:white; border:none; border-radius:4px; cursor:pointer; }
button:hover { background:#167d94; }
.form-group { display:flex; flex-direction:column; margin-top:10px; }
h2,h3 { color:#2099b6; }

#log { margin-top:10px; height:auto; background:white; border:1px solid #ccc; padding:10px; white-space:pre-wrap; font-family: monospace; }
</style>
</head>

<body>

<!-- ============================
     Bannière
============================= -->
<div class="banniere-container">
    <img src="{{ url_for('static', filename='images/notification.jpg') }}" alt="Bannière">
</div>

<!-- ============================
     Sidebar
============================= -->
<aside class="sidebar">
    <a href="/">Accueil</a>
    {% if modules.get("Ingestion") %}<a href="/ingestion">Ingestion</a>{% endif %}
    {% if modules.get("Apurement") %}<a href="/traitement/editor">Apurement</a>{% endif %}
    {% if modules.get("Croisement") %}<a href="/analyse">Croisement</a>{% endif %}
    {% if modules.get("Orientation") %}<a href="/exploitation">Orientation</a>{% endif %}
    {% if modules.get("Valorisation") %}<a href="/valorisation">Valorisation</a>{% endif %}
    {% if modules.get("Restitution") %}<a href="/notification">Restitution</a>{% endif %}
    <a href="/administration">Administration</a>
</aside>

<!-- ============================
     Contenu principal
============================= -->
<main class="main-content">

<h2>ADMINISTRATION</h2>

<hr>

<h3>Gestion des Templates</h3>
<label>Choisir le template</label>
<select id="templateSelect"></select>
<button onclick="downloadTemplate()">Télécharger le template</button>

<div class="form-group">
    <label>Sélectionner sur votre disque</label>
    <input type="file" id="fileTemplateInput" accept=".docx">
</div>

<button onclick="updateTemplate()">Actualiser le template</button>

<hr>

<h3>Gestion des Référentiels</h3>
<label>Choisir le référentiel</label>
<select id="fichierSelect"></select>
<button onclick="downloadFichier()">Télécharger le référentiel</button>

<div class="form-group">
    <label>Sélectionner sur votre disque</label>
    <input type="file" id="fileFichierInput" accept=".docx">
</div>

<button onclick="updateFichier()">Actualiser le référentiel</button>

<div id="log"></div>

</main>

<script>
// ============================
// Ajustement bannière dynamique
// ============================
function adjustLayout() {
    const banner = document.querySelector(".banniere-container");
    if(banner){
        const height = banner.offsetHeight + "px";
        document.documentElement.style.setProperty("--banner-height", height);
    }
}
window.addEventListener("load", adjustLayout);
window.addEventListener("resize", adjustLayout);

// ============================
// Chargement des listes
// ============================
async function loadTemplates() {
    const res = await fetch("/administration/api/templates");
    const data = await res.json();
    const select = document.getElementById("templateSelect");
    select.innerHTML = "<option value=''>-- Sélectionner --</option>";
    data.forEach(f => select.innerHTML += `<option value="${f}">${f}</option>`);
}

async function loadFichiers() {
    const res = await fetch("/administration/api/fichiers");
    const data = await res.json();
    const select = document.getElementById("fichierSelect");
    select.innerHTML = "<option value=''>-- Sélectionner --</option>";
    data.forEach(f => select.innerHTML += `<option value="${f}">${f}</option>`);
}

// ============================
// Télécharger
// ============================
function downloadTemplate() {
    const filename = document.getElementById("templateSelect").value;
    if(!filename){ alert("Sélectionnez un template"); return; }
    window.location.href = `/administration/download/template/${encodeURIComponent(filename)}`;
}

function downloadFichier() {
    const filename = document.getElementById("fichierSelect").value;
    if(!filename){ alert("Sélectionnez un fichier"); return; }
    window.location.href = `/administration/download/fichier/${encodeURIComponent(filename)}`;
}

// ============================
// Actualiser
// ============================
async function updateTemplate() {
    const fileInput = document.getElementById("fileTemplateInput");
    const filename = document.getElementById("templateSelect").value;
    const log = document.getElementById("log");
    if(!fileInput.files.length || !filename){ log.textContent="❌ Sélectionnez un fichier et un template"; return; }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    log.textContent="⏳ Actualisation en cours...";
    try {
        const res = await fetch(`/administration/update/template/${encodeURIComponent(filename)}`, {method:"POST", body: formData});
        const result = await res.json();
        log.textContent = result.success ? "✅ "+result.message : "❌ "+result.message;
        loadTemplates();
    } catch(e){ log.textContent="❌ Erreur : "+e.message; }
}

async function updateFichier() {
    const fileInput = document.getElementById("fileFichierInput");
    const filename = document.getElementById("fichierSelect").value;
    const log = document.getElementById("log");
    if(!fileInput.files.length || !filename){ log.textContent="❌ Sélectionnez un fichier et un référentiel"; return; }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    log.textContent="⏳ Actualisation en cours...";
    try {
        const res = await fetch(`/administration/update/fichier/${encodeURIComponent(filename)}`, {method:"POST", body: formData});
        const result = await res.json();
        log.textContent = result.success ? "✅ "+result.message : "❌ "+result.message;
        loadFichiers();
    } catch(e){ log.textContent="❌ Erreur : "+e.message; }
}

// ============================
// Init
// ============================
document.addEventListener("DOMContentLoaded", ()=>{
    loadTemplates();
    loadFichiers();
});
</script>

</body>
</html>

#
# modules\administration\routes.py
#

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
    
#
# modules\administration\services.py
#

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ==========================
# Gestion des Templates
# ==========================
TEMPLATES_DIR = os.path.join("data", "Templates")


def list_templates():
    """Renvoie la liste des fichiers dans data/Templates"""
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    list_templates.directory = TEMPLATES_DIR  # pour téléchargement
    return [f for f in os.listdir(TEMPLATES_DIR) if os.path.isfile(os.path.join(TEMPLATES_DIR, f))]

def save_template(filename, file):
    """Enregistre ou remplace un fichier template"""
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    path = os.path.join(TEMPLATES_DIR, filename)
    file.save(path)
    return {"success": True, "message": f"Template '{filename}' mis à jour avec succès"}

# ==========================
# Gestion des Fichiers
# ==========================
FICHIERS_DIR = os.path.join("data", "Fichier")

def list_fichiers():
    """Renvoie la liste des fichiers dans data/Fichier"""
    os.makedirs(FICHIERS_DIR, exist_ok=True)
    list_fichiers.directory = FICHIERS_DIR
    return [f for f in os.listdir(FICHIERS_DIR) if os.path.isfile(os.path.join(FICHIERS_DIR, f))]

def save_fichier(filename, file):
    """Enregistre ou remplace un fichier référentiel"""
    os.makedirs(FICHIERS_DIR, exist_ok=True)
    path = os.path.join(FICHIERS_DIR, filename)
    file.save(path)
    return {"success": True, "message": f"Référentiel '{filename}' mis à jour avec succès"}