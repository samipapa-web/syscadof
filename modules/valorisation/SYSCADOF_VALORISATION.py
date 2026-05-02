#
# MODULE 5: VALORISATION
#############################################
#

# modules\valorisation\templates\valorisation.html
#----------------------------------------------------------

<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>SYSCADOF - valorisation</title>

<script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.15.0/ace.js"></script>

<style>
/* =========================
   Styles généraux
   ========================= */
html, body {
    margin:0;
    padding:0;
    font-family: Arial, sans-serif;
    background:#f3f4f6;
}

/* Bannière fixe */
.banniere-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    z-index: 1000;
}
.banniere-container img {
    width:100%;
    display:block;
}

/* Hauteur dynamique de la bannière */
:root {
    --banner-height: 0px;
}

/* Sidebar fixe */
.sidebar {
    position: fixed;
    top: var(--banner-height);
    left: 0;
    bottom: 0;
    width: 110px;
    background-color: #1e293b;
    padding-top: 10px;
    overflow-y: auto;
}
.sidebar a {
    display: block;
    margin: 10px;
    padding: 10px 5px;
    text-align: center;
    color: white;
    text-decoration: none;
    font-weight: bold;
    border-radius: 4px;
    background-color: #127291;
    font-size: 12px;
}
.sidebar a:hover { background-color: #0d5a72; }

/* Contenu principal */
.main-content {
    margin-left: 110px;
    padding: 20px;
    padding-top: calc(20px + var(--banner-height));
    overflow-x: auto;
}

/* Titres */
h3 { color:#2099b6; }

/* Formulaire */
select, input { padding:6px; margin:5px 0; width:100%; }
button {
    padding:6px 12px;
    background:#2099b6;
    color:white;
    border:none;
    cursor:pointer;
    border-radius:4px;
    margin-top:5px;
}
button:hover { background:#167d94; }

#editor { width:100%; height:300px; margin-top:10px; border:1px solid #ccc; }
#log { margin-top:10px; height:50px; background:white; border:1px solid #ccc; padding:10px; overflow-y:auto; white-space:pre-wrap; font-family: monospace; }

/* Tableau */
table { width:100%; border-collapse: collapse; margin-top:20px; background:white; }
th { background:#2099b6; color:white; padding:10px; text-align:center; }
td { padding:8px; border-bottom:1px solid #ddd; text-align:center; }

/* Séparateur et formulaire */
.separator { border: none; border-top: 2px solid #2099b6; margin: 40px 0 10px 0; }
.form-grid { display: flex; flex-direction: column; gap: 12px; margin-top: 15px; margin-bottom: 15px; }
.form-row { display: grid; grid-template-columns: 230px 1fr; align-items: center; gap: 15px; }
.form-row label { font-weight: bold; text-align: left; }
.form-row select { width: 100%; }

/* Cellules ID */
.id-cell span {
    display: inline-block;
    padding: 4px 8px;
    background-color: #2099b6;
    color: white;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    text-decoration: none;
}
</style>
</head>

<body>

<!-- Bannière fixe -->
<div class="banniere-container">
    <img src="{{ url_for('static', filename='images/exploitation_s2.jpg') }}" alt="valorisation">
</div>

<!-- Sidebar fixe -->
<aside class="sidebar">
    <a href="/">Accueil</a>
    {% if modules.get("Ingestion") %}<a href="/ingestion">Ingestion</a>{% endif %}
    {% if modules.get("Apurement") %}<a href="/traitement/editor">Apurement</a>{% endif %}
    {% if modules.get("Croisement") %}<a href="/analyse">Croisement</a>{% endif %}
    {% if modules.get("Orientation") %}<a href="/exploitation">Orientation</a>{% endif %}
    {% if modules.get("Valorisation") %}<a href="/valorisation">Valorisation</a>{% endif %}
    {% if modules.get("Restitution") %}<a href="/notification">Restitution</a>{% endif %}
</aside>

<!-- Contenu principal -->
<div class="page-container">
<main class="main-content">

<h3>Paramétrage de l'exploitation</h3>

<div class="form-grid">
    <div class="form-row">
        <label for="fichierSelect">Fichier à exploiter</label>
        <select id="fichierSelect"></select>
    </div>
    <div class="form-row">
        <label for="matiereSelect">Matière recoupée</label>
        <select id="matiereSelect"></select>
    </div>
    <div class="form-row">
        <label for="chapitreSelect">Famille de risque</label>
        <select id="chapitreSelect"></select>
    </div>
    <div class="form-row">
        <label for="risqueSelect">Risque</label>
        <select id="risqueSelect"></select>
    </div>
    <div class="form-row">
        <label for="axeSelect">Axe de risque</label>
        <select id="axeSelect"></select>
    </div>
    <div class="form-row">
        <label for="impotsSelect">Impôts à inclure</label>
        <select id="impotsSelect" multiple>
            <option value="TVA">TVA</option>
            <option value="IS">IS</option>
            <option value="IRPP">IRPP</option>
            <option value="IRCM">IRCM</option>
            <option value="Autre_taxe">Autre_taxe</option>
        </select>
    </div>
    <div class="form-row">
        <label for="autreTaxeInput">Intitulé de Autre_taxe</label>
        <input type="text" id="autreTaxeInput" placeholder="Nom de l'autre taxe">
    </div>
    <div class="form-row">
        <label for="scriptSelect">Script d'exploitation</label>
        <select id="scriptSelect"></select>
    </div>
</div>

<button onclick="loadScript()">Charger le script</button>
<div id="editor"></div>
<input type="text" id="scriptName" placeholder="Nom du script modifié">
<button onclick="saveScript()">Sauvegarder le script</button>
<button onclick="executeScript()">Exécuter le script</button>

<div id="log"></div>
<hr class="separator">

<h3>Historique des travaux</h3>
<table>
<thead>
<tr>
<th>ID</th>
<th>Fichier généré</th>
<th>Risque</th>
<th>Axe</th>
<th>Impôts inclus</th>
<th>Responsable</th>
<th>Date</th>
</tr>
</thead>
<tbody id="historiqueBody"></tbody>
</table>

</main>
</div>

<script>
// Ajustement dynamique bannière
function adjustLayout(){
    const banner = document.querySelector(".banniere-container");
    if(banner){
        const height = banner.offsetHeight + "px";
        document.documentElement.style.setProperty("--banner-height", height);
    }
}
window.addEventListener("load", adjustLayout);
window.addEventListener("resize", adjustLayout);

// Ace editor
const editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.session.setMode("ace/mode/python");

// Chargement initial
document.addEventListener("DOMContentLoaded", () => {
    loadAllSelects();
    loadHistorique();
});

// Fonctions de selects, scripts et historique (inchangées)
async function loadAllSelects() {
    const res = await fetch("/valorisation/api/init");
    const data = await res.json();
    populateSelect("fichierSelect", data.fichiers);
    populateSelect("matiereSelect", data.matieres);
    populateSelect("chapitreSelect", data.chapitres);
    populateSelect("scriptSelect", data.scripts);
}
function populateSelect(id, items) {
    const select = document.getElementById(id);
    select.innerHTML = "<option value=''>-- Sélectionner --</option>";
    items.forEach(i => select.innerHTML += `<option value="${i}">${i}</option>`);
}
document.getElementById("chapitreSelect").addEventListener("change", loadRisques);
document.getElementById("risqueSelect").addEventListener("change", loadAxes);
async function loadRisques() {
    const chapitre = document.getElementById("chapitreSelect").value;
    const res = await fetch("/valorisation/api/risques?chapitre=" + encodeURIComponent(chapitre));
    const data = await res.json();
    populateSelect("risqueSelect", data);
}
async function loadAxes() {
    const chapitre = document.getElementById("chapitreSelect").value;
    const risque = document.getElementById("risqueSelect").value;
    const res = await fetch(`/valorisation/api/axes?chapitre=${encodeURIComponent(chapitre)}&risque=${encodeURIComponent(risque)}`);
    const data = await res.json();
    populateSelect("axeSelect", data);
}
async function loadScript() {
    const script = document.getElementById("scriptSelect").value;
    if(!script) return;
    const res = await fetch("/valorisation/api/load-script?name=" + encodeURIComponent(script));
    const data = await res.json();
    editor.setValue(data.content,-1);
}
async function saveScript() {
    const name = document.getElementById("scriptName").value;
    const content = editor.getValue();
    const res = await fetch("/valorisation/api/save-script", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({name, content})
    });
    const result = await res.json();
    document.getElementById("log").textContent = result.message || "Script sauvegardé.";
    loadAllSelects();
}
async function executeScript() {
    const log = document.getElementById("log");
    const impotsSelected = Array.from(document.getElementById("impotsSelect").selectedOptions).map(o=>o.value);
    const autreTaxe = document.getElementById("autreTaxeInput").value;
    const payload = {
        fichier: document.getElementById("fichierSelect").value,
        matiere: document.getElementById("matiereSelect").value,
        chapitre: document.getElementById("chapitreSelect").value,
        risque: document.getElementById("risqueSelect").value,
        axe: document.getElementById("axeSelect").value,
        script: editor.getValue(),
        impots: impotsSelected,
        autre_taxe: autreTaxe
    };
    log.textContent = "⏳ Exécution en cours...";
    try {
        const res = await fetch("/valorisation/api/execute", {
            method: "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify(payload)
        });
        const result = await res.json();
        log.textContent = result.success ? "✅ "+(result.message||"Script exécuté") : "❌ "+(result.message||"Erreur inconnue");
        loadHistorique();
    } catch(e){ log.textContent = "❌ Erreur réseau ou serveur : "+e.message; }
}
async function loadHistorique() {
    const res = await fetch("/valorisation/api/historique");
    const data = await res.json();
    const body = document.getElementById("historiqueBody");
    body.innerHTML="";
    data.forEach(r=>{
        body.innerHTML+=`
        <tr>
            <td class="id-cell"><span><a href="/analyse/tableur_analyse/${r.nom_fichier}" target="_blank" style="color:white;text-decoration:none;">${r.id}</a></span></td>
            <td>${r.nom_fichier}</td>
            <td>${r.risque}</td>
            <td>${r.axe}</td>
            <td>${r.impots_inclus||''}</td>
            <td>${r.utilisateur||"system"}</td>
            <td>${r.date_generation}</td>
        </tr>`;
    });
}
document.getElementById("historiqueBody").addEventListener("click", function(e){
    const cell = e.target.closest(".id-cell");
    if(!cell) return;
    const filename = cell.dataset.filename;
    if(!filename) return;
    // window.open(`/analyse/tableur_analyse/${filename}`,"_blank");
	window.location.href = `/analyse/tableur_analyse/${filename}`;
});
</script>

</body>
</html>


# modules\valorisation\routes.py
#----------------------------------------------------------

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

# ===============================
# PAGE PRINCIPALE
# ===============================
@valorisation_bp.route("/")
def valorisation():
    return render_template("valorisation.html")


# ===============================
# INITIALISATION
# ===============================
@valorisation_bp.route("/api/init")
def api_init():
    return jsonify({
        "fichiers": get_recent_exploiter_files(),
        "matieres": get_matieres(),
        "chapitres": get_chapitres(),
        "scripts": list_scripts()
    })


# ===============================
# RISQUES
# ===============================
@valorisation_bp.route("/api/risques")
def api_risques():
    chapitre = request.args.get("chapitre")
    return jsonify(get_risques_by_chapitre(chapitre))


# ===============================
# AXES
# ===============================
@valorisation_bp.route("/api/axes")
def api_axes():
    chapitre = request.args.get("chapitre")
    risque = request.args.get("risque")
    return jsonify(get_axes(chapitre, risque))


# ===============================
# SCRIPTS
# ===============================
@valorisation_bp.route("/api/load-script")
def api_load_script():
    name = request.args.get("name")
    return jsonify({"content": load_script_content(name)})


@valorisation_bp.route("/api/save-script", methods=["POST"])
def api_save_script():
    data = request.json
    return jsonify(save_script_file(data["name"], data["content"]))


# ===============================
# EXECUTION
# ===============================
@valorisation_bp.route("/api/execute", methods=["POST"])
def api_execute():
    data = request.json
    utilisateur = session.get("user", "system")

    result = execute_valorisation_process(
        fichier=data["fichier"],
        matiere=data["matiere"],
        chapitre=data["chapitre"],
        risque=data["risque"],
        axe=data["axe"],
        script=data["script"],
        impots_inclus=data.get("impots", []),
        autre_taxe=data.get("autre_taxe", ""),
        utilisateur=utilisateur
    )

    return jsonify(result)


# ===============================
# HISTORIQUE
# ===============================
@valorisation_bp.route("/api/historique")
def api_historique():
    return jsonify(get_historique())


# ===============================
# VISUALISATION TABLEUR
# ===============================
@valorisation_bp.route("/tableur_analyse/<path:filename>")
def tableur_analyse(filename):

    safe_filename = secure_filename(filename)
    sortie_dir = current_app.config["SORTIE_DIR"]

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
	

# Modules/valorisation/services.py
#--------------------------------------------------------

import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from psycopg2.extras import RealDictCursor
from flask import current_app

import pandas as pd

from database import get_connection, release_connection
from .scripts.script_valorisation import traitement_valorisation


# =========================================================
# SAFE DIRECTORY (RENDER FIX)
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

    finally:
        release_connection(conn)


# =========================================================
# FILES
# =========================================================
def get_recent_exploiter_files():
    path = safe_output_dir()

    files = [
        f for f in os.listdir(path)
        if f.lower().startswith("exploiter") and f.endswith(".xlsx")
    ]

    files.sort(reverse=True)
    return files[:20]


# =========================================================
# MATIERES
# =========================================================
def get_matieres():
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT matiere_recoupee
            FROM matieres
            WHERE matiere_recoupee IS NOT NULL
            ORDER BY matiere_recoupee
        """)

        return [r["matiere_recoupee"] for r in cur.fetchall()]

    finally:
        release_connection(conn)


# =========================================================
# CHAPITRES
# =========================================================
def get_chapitres():
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT DISTINCT chapitre
            FROM risques
            WHERE chapitre IS NOT NULL
            ORDER BY chapitre
        """)

        return [r["chapitre"] for r in cur.fetchall()]

    finally:
        release_connection(conn)


# =========================================================
# RISQUES
# =========================================================
def get_risques_by_chapitre(chapitre):
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT DISTINCT risque
            FROM risques
            WHERE LOWER(chapitre) = LOWER(%s)
            ORDER BY risque
        """, (chapitre,))

        return [r["risque"] for r in cur.fetchall()]

    finally:
        release_connection(conn)


# =========================================================
# AXES
# =========================================================
def get_axes(chapitre, risque):
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT axe
            FROM risques
            WHERE LOWER(chapitre) = LOWER(%s)
              AND LOWER(risque) = LOWER(%s)
            ORDER BY axe
        """, (chapitre, risque))

        return [r["axe"] for r in cur.fetchall()]

    finally:
        release_connection(conn)


# =========================================================
# SCRIPTS
# =========================================================
def list_scripts():
    path = current_app.config["VALO_SCRIPT_DIR"]
    return [f for f in os.listdir(path) if f.endswith(".py")]


def load_script_content(name):
    path = os.path.join(current_app.config["VALO_SCRIPT_DIR"], secure_filename(name))

    if not os.path.exists(path):
        return ""

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_script_file(name, content):
    path_dir = current_app.config["VALO_SCRIPT_DIR"]
    os.makedirs(path_dir, exist_ok=True)

    filename = secure_filename(name)
    if not filename.endswith(".py"):
        filename += ".py"

    path = os.path.join(path_dir, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return {"success": True, "message": "Script sauvegardé"}


# =========================================================
# EXECUTION
# =========================================================
def execute_valorisation_process(
    fichier, matiere, chapitre, risque, axe,
    script, impots_inclus, autre_taxe, utilisateur="system"
):
    try:
        fichier = secure_filename(fichier)

        historique_id = uuid.uuid4().int >> 64

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
        try:
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO valorisation (
                    nom_fichier, chapitre, risque, axe,
                    script_utilise, utilisateur, impots_inclus, date_generation
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
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

        finally:
            release_connection(conn)

        return {"success": True, "message": result["message"]}

    except Exception:
        return {
            "success": False,
            "message": "Erreur interne du traitement"
        }


# =========================================================
# HISTORIQUE
# =========================================================
def get_historique():
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM valorisation
            ORDER BY id DESC
        """)

        return cur.fetchall()

    finally:
        release_connection(conn)

#
# modules/valorisation/__init__.py
#--------------------------------------------------

from flask import Blueprint
from .services import init_valorisation_table

valorisation_bp = Blueprint(
    "valorisation",
    __name__,
    url_prefix="/valorisation",
    template_folder="templates",
    static_folder="static"
)

init_valorisation_table()

from . import routes


#
# modules\valorisation\insert_scripts.py
#-------------------------------------------------------

import os

def list_scripts(scripts_dir):
    scripts = []
    if os.path.exists(scripts_dir):
        for f in os.listdir(scripts_dir):
            if f.endswith(".py"):
                scripts.append({"id": f, "titre": f.replace(".py", ""), "auteur": "Admin"})
    return scripts

def load_script(scripts_dir, script_name):
    script_path = os.path.join(scripts_dir, script_name)
    if not os.path.exists(script_path):
        return "", False, "Script introuvable"
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content, True, None

def save_script(scripts_dir, titre, contenu):
    if not os.path.exists(scripts_dir):
        os.makedirs(scripts_dir)
    filename = f"{titre}.py"
    path = os.path.join(scripts_dir, filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(contenu)
        return True, f"Script sauvegardé : {filename}", None
    except Exception as e:
        return False, "", str(e)

# modules\valorisation\scripts\script_valorisation.py
#-----------------------------------------------
#le bouton "Executer le script" de la page valorisation.html lance l'execution de ce script_valorisation.py

# modules/valorisation/scripts/script_valorisation.py
# ------------------------------------------------------

import os
import pandas as pd
import numpy as np
from datetime import datetime

from database import get_connection
from config import SORTIE_DIR


# ===============================
# OUTIL: NORMALISATION COLONNES
# ===============================
def normalize_columns(df):
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.upper()
        .str.replace(" ", "_")
        .str.replace("É", "E")
        .str.replace("È", "E")
        .str.replace("Ê", "E")
        .str.replace("À", "A")
    )
    return df


# ===============================
# TRAITEMENT PRINCIPAL
# ===============================
def traitement_valorisation(
        fichier,
        matiere,
        risque,
        axe,
        historique_id,
        impots_inclus,
        autre_taxe=""
):

    conn = None
    cur = None

    try:
        # --------------------------
        # Sécurité dossier sortie
        # --------------------------
        os.makedirs(SORTIE_DIR, exist_ok=True)

        chemin_source = os.path.join(SORTIE_DIR, fichier)

        if not os.path.exists(chemin_source):
            raise FileNotFoundError(f"Fichier introuvable : {fichier}")

        # --------------------------
        # Lecture Excel robuste
        # --------------------------
        df = pd.read_excel(chemin_source, dtype=str)
        df = normalize_columns(df)

        # Conversion numérique safe
        def to_num(col):
            return pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)

        df["VAL_RECOUP"] = to_num("TOTAL_GENERAL")
        df["VAL_DECLA"] = to_num("ACHATS_HORS_REGION_MARCH")
        df["ECART_NOTIF"] = to_num("ECART")

        # --------------------------
        # DB CONNECTION SAFE
        # --------------------------
        conn = get_connection()
        cur = conn.cursor()

        # --------------------------
        # NIU
        # --------------------------
        cur.execute("""
            SELECT niu, raison_sociale, sigle, activite,
                   regime, centre, etat, telephone
            FROM niu
        """)
        df_niu = pd.DataFrame(cur.fetchall())

        if not df_niu.empty:
            df_niu = normalize_columns(df_niu)
            df = df.merge(df_niu, on="NIU", how="left")

        # --------------------------
        # UG (FIX JOIN KEY)
        # --------------------------
        cur.execute("""
            SELECT centre, cdif, crif, cdia, cria,
                   acdi, acri, ville, directeur, regional
            FROM ug
        """)
        df_ug = pd.DataFrame(cur.fetchall())

        if not df_ug.empty:
            df_ug = normalize_columns(df_ug)

            if "CENTRE" in df.columns and "CENTRE" in df_ug.columns:
                df = df.merge(df_ug, on="CENTRE", how="left")

        # --------------------------
        # EXTRACTION IDA / IDB
        # --------------------------
        base = os.path.basename(fichier)
        bloc = base.replace("exploiter_", "").split("_")[0]

        try:
            ida, idb = bloc.split("X")
            IDA, IDB = int(ida), int(idb)
        except:
            raise ValueError(f"Nom fichier invalide : {fichier}")

        # --------------------------
        # SOURCES (ORDER SAFE)
        # --------------------------
        cur.execute("""
            SELECT * FROM sources_lac
            WHERE id = ANY(%s)
        """, ([IDA, IDB],))

        rows = cur.fetchall()
        sources = {r[0]: r for r in rows} if rows else {}

        if IDA not in sources or IDB not in sources:
            raise ValueError("Sources introuvables")

        source_a = sources[IDA]
        source_b = sources[IDB]

        # --------------------------
        # ENRICHISSEMENT
        # --------------------------
        df["SOURCE_A"] = source_a["intitule_source"]
        df["SOURCE_B"] = source_b["intitule_source"]
        df["PERIODE_A"] = source_a["annee"]
        df["PERIODE_B"] = source_b["annee"]
        df["PROVENANCE_A"] = source_a["fournisseur"]
        df["PROVENANCE_B"] = source_b["fournisseur"]

        # --------------------------
        # PARAMÈTRES MÉTIER
        # --------------------------
        annee = datetime.now().year

        df["PERIODE"] = str(annee)
        df["REF_NOTIF"] = f"UTTAD-{annee}-{historique_id:05d}"
        df["RISQUE"] = risque
        df["AXE"] = axe
        df["MATIERE"] = matiere
        df["LISTE_IMPOTS"] = ",".join(impots_inclus or [])
        df["AUTRE_TAXE"] = autre_taxe

        # --------------------------
        # BASE CALCUL
        # --------------------------
        df["MARGE"] = df["ECART_NOTIF"] * 0.2
        df["BASE"] = df["ECART_NOTIF"] + df["MARGE"]

        # ===============================
        # INIT TAXES
        # ===============================
        def init(prefix):
            for col in ["BASE", "TAUX", "PRINCI", "PENAL", "TOTAL"]:
                df[f"{prefix}_{col}"] = 0

        # ===============================
        # TVA
        # ===============================
        init("TVA")
        if "TVA" in impots_inclus:
            df["TVA_BASE"] = df["BASE"]
            df["TVA_TAUX"] = 19.25
            df["TVA_PRINCI"] = df["BASE"] * 0.1925
            df["TVA_PENAL"] = df["TVA_PRINCI"] * 0.3
            df["TVA_TOTAL"] = df["TVA_PRINCI"] + df["TVA_PENAL"]

        # ===============================
        # IS
        # ===============================
        init("IS")
        if "IS" in impots_inclus:
            niu = df.get("NIU", "").astype(str)
            centre = df.get("CENTRE", "").astype(str)

            df["IS_BASE"] = np.where(niu.str.startswith("P"), 0, df["BASE"])
            df["IS_TAUX"] = np.where(centre.str.startswith("DGE"), 33, 27.5)

            df["IS_PRINCI"] = df["IS_BASE"] * df["IS_TAUX"] / 100
            df["IS_PENAL"] = df["IS_PRINCI"] * 0.3
            df["IS_TOTAL"] = df["IS_PRINCI"] + df["IS_PENAL"]

        # ===============================
        # IRPP
        # ===============================
        init("IRPP")
        if "IRPP" in impots_inclus:

            niu = df.get("NIU", "").astype(str)
            base_irpp = np.where(niu.str.startswith("M"), 0, df["BASE"])

            SNT = np.maximum(base_irpp - 500000, 0)

            IRPP = np.select(
                [
                    SNT <= 0,
                    SNT <= 2000000,
                    SNT <= 3000000,
                    SNT <= 5000000,
                    SNT > 5000000
                ],
                [
                    0,
                    SNT * 0.10,
                    2000000*0.10 + (SNT-2000000)*0.15,
                    2000000*0.10 + 1000000*0.15 + (SNT-3000000)*0.25,
                    2000000*0.10 + 1000000*0.15 + 2000000*0.25 + (SNT-5000000)*0.35
                ]
            )

            df["IRPP_PRINCI"] = IRPP
            df["IRPP_PENAL"] = IRPP * 0.3
            df["IRPP_TOTAL"] = df["IRPP_PRINCI"] + df["IRPP_PENAL"]

        # ===============================
        # IRCM
        # ===============================
        init("IRCM")
        if "IRCM" in impots_inclus:
            df["IRCM_BASE"] = df["BASE"] - df.get("IS_PRINCI", 0) - df.get("IRPP_PRINCI", 0)
            df["IRCM_TAUX"] = 16.5
            df["IRCM_PRINCI"] = df["IRCM_BASE"] * 0.165
            df["IRCM_PENAL"] = df["IRCM_PRINCI"] * 0.3
            df["IRCM_TOTAL"] = df["IRCM_PRINCI"] + df["IRCM_PENAL"]

        # ===============================
        # AUTRE TAXE
        # ===============================
        if "Autre_taxe" in impots_inclus and autre_taxe:
            p = autre_taxe.upper()
            init(p)

            df[f"{p}_BASE"] = df["BASE"]
            df[f"{p}_TAUX"] = 5
            df[f"{p}_PRINCI"] = df["BASE"] * 0.05
            df[f"{p}_PENAL"] = df[f"{p}_PRINCI"] * 0.3
            df[f"{p}_TOTAL"] = df[f"{p}_PRINCI"] + df[f"{p}_PENAL"]

        # ===============================
        # TOTAUX
        # ===============================
        df["TAX_PRINCI"] = df.filter(like="_PRINCI").sum(axis=1)
        df["TAX_PENAL"] = df.filter(like="_PENAL").sum(axis=1)
        df["TAX_TOTAL"] = df["TAX_PRINCI"] + df["TAX_PENAL"]

        # --------------------------
        # OUTPUT
        # --------------------------
        nouveau_nom = fichier.replace("exploiter", "Output")
        chemin_sortie = os.path.join(SORTIE_DIR, nouveau_nom)

        df.to_excel(chemin_sortie, index=False)

        return {
            "message": "Restitution générée avec succès.",
            "fichier_genere": nouveau_nom
        }

    except Exception as e:
        return {
            "message": f"Erreur : {str(e)}",
            "fichier_genere": None
        }

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
            
 
 
 # database.py
# ------------------------------------------------------------------

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

# =========================================================
# CONFIGURATION POSTGRESQL (PRODUCTION SAFE)
# =========================================================

def _get_env(name):
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Variable d'environnement manquante : {name}")
    return value


DB_CONFIG = {
    "host": _get_env("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": _get_env("DB_NAME"),
    "user": _get_env("DB_USER"),
    "password": _get_env("DB_PASSWORD")
}

# =========================================================
# POOL DE CONNEXION (IMPORTANT POUR RENDER)
# =========================================================

db_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    **DB_CONFIG
)


def get_connection():
    """
    Retourne une connexion PostgreSQL (pool).
    """
    conn = db_pool.getconn()
    conn.cursor_factory = RealDictCursor
    return conn


def release_connection(conn):
    """
    Rend la connexion au pool.
    """
    if conn:
        db_pool.putconn(conn)
        
# config.py
# ========================================
import os

# =========================================================
# BASE_DIR et DATA_DIR
# =========================================================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# =========================================================
# DATA_DIR dynamique (local vs production)
# =========================================================
DATA_DIR = os.getenv("DATA_DIR", os.path.join(BASE_DIR, "data"))

# Sous-dossiers
DATA_LAC_DIR = os.path.join(DATA_DIR, "LAC")
DATA_CLEAN_DIR = os.path.join(DATA_DIR, "clean")
SORTIE_DIR = os.path.join(DATA_DIR, "Sortie")
TEMPLATES_DIR = os.path.join(DATA_DIR, "Templates")

#Fichier excel de references
REF_PATH = os.path.join(BASE_DIR, "data", "Templates", "REFERENCES.xlsx")


# Scripts des modules
APUR_SCRIPT_DIR = os.path.join(BASE_DIR, "modules", "traitement", "scripts")
ANAL_SCRIPT_DIR = os.path.join(BASE_DIR, "modules", "analyse", "scripts")
VALO_SCRIPT_DIR = os.path.join(BASE_DIR, "modules", "valorisation", "scripts")
NOTI_SCRIPT_DIR = os.path.join(BASE_DIR, "modules", "notification", "scripts")



# =========================================================
# Création des dossiers si inexistants
# =========================================================

for folder in [DATA_LAC_DIR, DATA_CLEAN_DIR, TEMPLATES_DIR, SORTIE_DIR]:
    try:
        os.makedirs(folder, exist_ok=True)
    except PermissionError:
        print(f"⚠️ Impossible de créer le dossier {folder}, vérifiez les permissions.")
    

# =========================================================
# Paramètres généraux
# =========================================================
ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls", "txt"}
VALID_TEMPORALITES = ["Stock", "Flux annuel", "Flux mensuel"]

# =========================================================
# Débogage Render : afficher les chemins
# =========================================================
print(f"DATA_DIR = {DATA_DIR}")
print(f"DATA_LAC_DIR = {DATA_LAC_DIR}")
print(f"DATA_CLEAN_DIR = {DATA_CLEAN_DIR}")
print(f"SORTIE_DIR = {SORTIE_DIR}")


