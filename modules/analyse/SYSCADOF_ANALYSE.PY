
## MODULE 3: CROISEMENT/ANALYSE
## -----------------------------------------------

# \modules\analyse\templates\analyse.html
#-----------------------------------

<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Croisement des données – Éditeur de scripts</title>

<script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.15.0/ace.js" crossorigin="anonymous"></script>

<style>
/* =========================
   Structure générale
========================= */
html, body{
    margin:0;
    padding:0;
}
body{
    font-family:Arial,sans-serif;
    background:#f3f4f6;
}

/* =========================
   Bannière fixée
========================= */
.banniere-container{
    position:fixed;
    top:0;
    left:0;
    width:100%;
    z-index:1000;
}
.banniere-container img{
    width:100%;
    display:block;
}

/* Variable dynamique */
:root{
    --banner-height:0px;
}

/* =========================
   Sidebar fixe
========================= */
.sidebar{
    position:fixed;
    top:var(--banner-height);
    left:0;
    bottom:0;
    width:110px;
    background-color:#1e293b;
    padding-top:10px;
    overflow-y:auto;
}
.sidebar a{
    display:block;
    margin:10px;
    padding:10px 5px;
    text-align:center;
    color:white;
    text-decoration:none;
    font-weight:bold;
    border-radius:4px;
    background-color:#127291;
    font-size:12px;
}
.sidebar a:hover{
    background-color:#0d5a72;
}

/* =========================
   Contenu principal
========================= */
.main-content{
    margin-left:110px;
    padding:20px;
    padding-top:calc(20px + var(--banner-height));
    overflow-x:auto;
}

/* =========================
   Formulaire
========================= */
label{
    font-weight:bold;
    display:block;
    margin-top:15px;
}
select,input,button{
    width:100%;
    padding:6px;
    margin-top:5px;
}
#editor{
    height:400px;
    border:1px solid #ccc;
    margin-top:15px;
}
#log{
    margin-top:15px;
    height:50px;
    background:white;
    border:1px solid #ccc;
    padding:10px;
    overflow-y:auto;
    white-space:pre-wrap;
}
button{
    background-color:#2099b6;
    color:white;
    border:none;
    cursor:pointer;
    margin-top:10px;
    border-radius:4px;
}
button:hover{
    background-color:#127291;
}

/* =========================
   Tableau historique
========================= */
table{
    border-collapse:collapse;
    width:100%;
    margin-top:20px;
}
table th, table td{
    border:1px solid #ccc;
    padding:6px;
    text-align:center;
}
table th{
    background-color:#2099b6;
    color:white;
    position:sticky;
    top:0;
    z-index:1;
}
td.type-cell span{
    display:inline-block;
    padding:4px 8px;
    background-color:#2099b6;
    color:white;
    border-radius:4px;
    cursor:pointer;
    font-size:0.9rem;
}
td:first-child, th:first-child{
    text-align:left;
}
</style>
</head>

<body>

<div class="banniere-container">
    <img src="{{ url_for('static', filename='images/analyse.jpg') }}" alt="Croisement">
</div>

<aside class="sidebar">

<a href="/">Accueil</a>

{% if modules.get("Ingestion") %}
<a href="/ingestion">Ingestion</a>
{% endif %}

{% if modules.get("Apurement") %}
<a href="/traitement/editor">Apurement</a>
{% endif %}

{% if modules.get("Croisement") %}
<a href="/analyse">Croisement</a>
{% endif %}

{% if modules.get("Orientation") %}
<a href="/exploitation">Orientation</a>
{% endif %}

{% if modules.get("Valorisation") %}
<a href="/valorisation">Valorisation</a>
{% endif %}

{% if modules.get("Restitution") %}
<a href="/notification">Restitution</a>
{% endif %}

</aside>

<main class="main-content">

<label>Source de données A</label>
<select id="sourceSelectA"></select>

<label>Source de données B</label>
<select id="sourceSelectB"></select>

<label>Script de croisement/analyse</label>
<select id="scriptSelect"></select>

<button id="loadScriptBtn">Charger le script</button>

<div id="editor"># Le script apparaîtra ici</div>

<label>Titre du nouveau script</label>
<input id="newScriptTitle" placeholder="Ex : Croisement TVA et CA">

<button id="saveScriptBtn">Sauvegarder comme nouveau script</button>
<button id="runScriptBtn">Exécuter le script</button>

<div id="log"></div>

<hr>

<label>Historique des croisements</label>

<table>
<thead>
<tr>
<th>ID A</th>
<th>ID B</th>
<th>Nom du fichier</th>
<th>Type</th>
<th>Utilisateur</th>
<th>Date</th>
</tr>
</thead>

<tbody id="historyTable">
{% for c in croisements %}
<tr>
<td>{{ c.id_source_a }}</td>
<td>{{ c.id_source_b }}</td>
<td>{{ c.nom_fichier }}</td>

<td class="type-cell">
<span class="open-tableur" data-filename="{{ c.nom_fichier }}">
{{ c.type_fichier }}
</span>
</td>

<td>{{ c.utilisateur }}</td>
<td>{{ c.date_stockage }}</td>

</tr>
{% endfor %}
</tbody>
</table>

</main>

<script>
/* =========================
   Ajustement dynamique bannière
========================= */
function adjustLayout(){
    const banner = document.querySelector(".banniere-container");
    if(banner){
        const height = banner.offsetHeight + "px";
        document.documentElement.style.setProperty("--banner-height", height);
    }
}
window.addEventListener("load", adjustLayout);
window.addEventListener("resize", adjustLayout);

/* =========================
   Ace editor
========================= */
const editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.session.setMode("ace/mode/python");

const log = document.getElementById("log");
const sourceSelectA = document.getElementById("sourceSelectA");
const sourceSelectB = document.getElementById("sourceSelectB");
const scriptSelect = document.getElementById("scriptSelect");

/* =========================
   Charger sources
========================= */
async function loadSourcesLac(){
    const res = await fetch("/analyse/api/sources-lac");
    const sources = await res.json();
    [sourceSelectA, sourceSelectB].forEach(select=>{
        select.innerHTML="";
        sources.forEach(s=>{
            const opt = document.createElement("option");
            opt.value = s.id;
            opt.textContent = `${s.intitule_source} (${s.annee || '-'}/${s.mois || '-'})`;
            select.appendChild(opt);
        });
    });
}

/* =========================
   Charger scripts
========================= */
async function loadScripts(){
    const res = await fetch("/analyse/api/scripts");
    const scripts = await res.json();
    scriptSelect.innerHTML="";
    scripts.forEach(s=>{
        const opt = document.createElement("option");
        opt.value=s.id;
        opt.textContent=s.titre;
        scriptSelect.appendChild(opt);
    });
}

/* =========================
   Charger script
========================= */
document.getElementById("loadScriptBtn").onclick = async ()=>{
    const id = scriptSelect.value;
    const res = await fetch(`/analyse/api/get-script/${id}`);
    const data = await res.json();
    log.textContent = data.success ? "✅ Script chargé." : "❌ " + data.error;
    if(data.success) editor.setValue(data.contenu,-1);
};

/* =========================
   Exécution script
========================= */
document.getElementById("runScriptBtn").onclick = async ()=>{
    if(!sourceSelectA.value || !sourceSelectB.value){
        log.textContent="❌ Sélectionner les deux sources.";
        return;
    }
    const formData=new FormData();
    formData.append("source_a_id",sourceSelectA.value);
    formData.append("source_b_id",sourceSelectB.value);
    formData.append("script_contenu",editor.getValue());
    log.textContent="⏳ Exécution...";
    const res = await fetch(`/analyse/api/run-script/${scriptSelect.value}`,{
        method:"POST",
        body:formData
    });
    const data = await res.json();
    log.textContent = data.success ? "✅ "+data.message : "❌ "+data.error;

    if(data.success){
        const tBody = document.getElementById("historyTable");
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${sourceSelectA.value}</td>
            <td>${sourceSelectB.value}</td>
            <td>${data.resultat_sortie}</td>
            <td class="type-cell">
                <span class="open-tableur" data-filename="${data.resultat_sortie}">
                    ${data.resultat_sortie.split('.').pop()}
                </span>
            </td>
            <td>${data.utilisateur || "system"}</td>
            <td>${new Date().toLocaleString()}</td>
        `;
        tBody.prepend(tr);
    }
};

/* =========================
   Sauvegarde script
========================= */
document.getElementById("saveScriptBtn").onclick = async ()=>{
    const titre=document.getElementById("newScriptTitle").value.trim();
    if(!titre){ log.textContent="❌ Titre requis."; return; }
    const res=await fetch("/analyse/api/save-new-script",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({titre:titre, contenu:editor.getValue()})
    });
    const data=await res.json();
    log.textContent=data.success ? "✅ "+data.message : "❌ "+data.error;
    loadScripts();
};

/* =========================
   Ouverture tableur (module analyse)
========================= */
document.getElementById("historyTable").addEventListener("click", function(e){
    const btn = e.target.closest(".open-tableur");
    if(!btn) return;
    const filename = btn.dataset.filename;
    if(!filename) return;
    const safe = encodeURIComponent(filename);
    // window.open(`/analyse/tableur_analyse/${safe}`, "_blank");
	window.location.href = `/analyse/tableur_analyse/${safe}`;
});

/* =========================
   Initialisation
========================= */
loadSourcesLac();
loadScripts();
</script>

</body>
</html>


# \modules\analyse\_init_.py
#-----------------------------------

from flask import Blueprint

analyse_bp = Blueprint(
    'analyse', __name__,
    template_folder='templates',
    static_folder='static'
)

from . import routes, services



# \modules\analyse\routes.py
#-----------------------------------

import os
import pandas as pd
import sys
from datetime import datetime

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

from .services import run_script
from . import analyse_bp

from database import get_connection

# =========================================================
# PAGE PRINCIPALE
# =========================================================
@analyse_bp.route("/")
def analyse_page():

    conn = get_connection()   # ✅ CORRIGÉ
    cur = conn.cursor()

    try:
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

        cur.execute("""
            SELECT * FROM croisements
            ORDER BY date_stockage DESC
        """)

        croisements = cur.fetchall()

    finally:
        cur.close()
        conn.close()

    return render_template("analyse.html", croisements=croisements)


# =========================================================
# SOURCES
# =========================================================
@analyse_bp.route("/api/sources-lac")
def list_sources_lac():

    conn = get_connection()   # ✅ CORRIGÉ
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT id, intitule_source, nom_fichier, annee, mois
            FROM sources_clean
            ORDER BY date_stockage DESC
        """)
        data = cur.fetchall()

    finally:
        cur.close()
        conn.close()

    return jsonify(data)


# =========================================================
# SCRIPTS
# =========================================================
@analyse_bp.route("/api/scripts")
def list_scripts():

    scripts_dir = current_app.config["ANAL_SCRIPT_DIR"]

    fichiers = [f for f in os.listdir(scripts_dir) if f.endswith(".py")]

    return jsonify([
        {"id": f, "titre": f.replace(".py", "")}
        for f in fichiers
    ])


# =========================================================
# CHARGER SCRIPT
# =========================================================
@analyse_bp.route("/api/get-script/<script_name>")
def get_script(script_name):

    scripts_dir = current_app.config["ANAL_SCRIPT_DIR"]

    if ".." in script_name:
        return jsonify(success=False, error="Nom invalide")

    chemin = os.path.join(scripts_dir, script_name)

    if not os.path.exists(chemin):
        return jsonify(success=False, error="Introuvable")

    with open(chemin, "r", encoding="utf-8") as f:
        contenu = f.read()

    return jsonify(success=True, contenu=contenu)


# =========================================================
# SAVE SCRIPT
# =========================================================
@analyse_bp.route("/api/save-new-script", methods=["POST"])
def save_new_script():

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


# =========================================================
# EXECUTION SCRIPT
# =========================================================
@analyse_bp.route("/api/run-script/<script_name>", methods=["POST"])
def execute(script_name):

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

    return jsonify(
        success=True,
        message=data.get("message"),
        resultat_sortie=data.get("resultat_sortie"),
        utilisateur=data.get("utilisateur")
    )


# =========================================================
# TABLEUR
# =========================================================
@analyse_bp.route("/tableur_analyse/<path:filename>")
def tableur_analyse(filename):

    safe = secure_filename(filename)

    sortie_dir = current_app.config["SORTIE_DIR"]
    path = os.path.join(sortie_dir, safe)

    if not os.path.exists(path):
        abort(404)

    try:
        if safe.endswith(".csv"):
            df = pd.read_csv(path)
        elif safe.endswith(".xlsx"):
            df = pd.read_excel(path, engine="openpyxl")
        else:
            abort(400)

    except Exception as e:
        abort(500, str(e))

    return render_template(
        "tableur_analyse.html",
        data=df.to_dict(orient="records"),
        columns=df.columns.tolist(),
        filename=safe
    )


# =========================================================
# DOWNLOAD
# =========================================================
@analyse_bp.route("/download/<path:filename>")
def download_sortie(filename):

    safe = secure_filename(filename)

    sortie_dir = current_app.config["SORTIE_DIR"]

    return send_from_directory(sortie_dir, safe, as_attachment=True)
    

#modules\analyse\services.py
#----------------------------------------------------------

import os
from datetime import datetime
from flask import current_app, session
from psycopg2.extras import RealDictCursor


# =========================================================
# CONNEXION CENTRALISÉE
# =========================================================
from database import get_connection

def get_conn():
    return get_connection()


# =========================================================
# EXÉCUTION SCRIPT ANALYSE
# =========================================================
def run_script(script_id, source_a_id, source_b_id, script_code=None):

    if not script_code:
        return False, {"error": "Script vide"}

    sortie_dir = current_app.config["SORTIE_DIR"]
    clean_dir = current_app.config.get("CLEAN_DIR")

    utilisateur = session.get("user", "system")

    # ✅ CORRECTION MAJEURE ICI
    exec_env = {
        "source_a_id": int(source_a_id),
        "source_b_id": int(source_b_id),
        "SORTIE_DIR": sortie_dir,
        "CLEAN_DIR": clean_dir,
        "session": session,
        "get_conn": get_conn,   # 🔥 INJECTION CRITIQUE
        "__builtins__": __builtins__,
    }

    try:
        exec(script_code, exec_env)

        dernier = exec_env.get("dernier_croisement")

        if not dernier:
            return False, {"error": "Le script n'a pas retourné 'dernier_croisement'"}

        nom_fichier = dernier.get("nom_fichier")
        type_fichier = dernier.get("type_fichier", "xlsx")

        if not nom_fichier:
            return False, {"error": "nom_fichier manquant"}

        conn = get_conn()
        cur = conn.cursor()

        try:
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

            cur.execute("""
                INSERT INTO croisements
                (id_source_a, id_source_b, nom_fichier, type_fichier, utilisateur, date_stockage)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                dernier.get("id_source_a"),
                dernier.get("id_source_b"),
                nom_fichier,
                type_fichier,
                dernier.get("utilisateur", utilisateur),
                datetime.now()
            ))

            conn.commit()

        finally:
            cur.close()
            conn.close()

        return True, {
            "message": f"Fichier généré : {nom_fichier}",
            "resultat_sortie": nom_fichier,
            "utilisateur": dernier.get("utilisateur", utilisateur)
        }

    except Exception as e:
        return False, {"error": f"Erreur exécution script : {str(e)}"}

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

        
# modules\analyse\scripts\analyse_script_type.py
#------------------------------------------------------
# Ce script est execute en cliquant sur le bouton "Executer le script" de la page analyse.html
# 

# script_analyse_type.py

import os
import pandas as pd
from openpyxl import load_workbook
from datetime import datetime
from psycopg2.extras import RealDictCursor

# ==============================
# VARIABLES INJECTÉES
# ==============================
source_a_id = globals().get("source_a_id")
source_b_id = globals().get("source_b_id")
SORTIE_DIR = globals().get("SORTIE_DIR")
CLEAN_DIR = globals().get("CLEAN_DIR")  # ✅ corrigé
session = globals().get("session", {})
get_conn = globals().get("get_conn")

if not CLEAN_DIR:
    raise Exception("CLEAN_DIR non défini")

if not SORTIE_DIR:
    raise Exception("SORTIE_DIR non défini")

# Fallback connexion DB
if not get_conn:
    try:
        from database import get_connection
        get_conn = get_connection
    except Exception:
        raise Exception("Connexion DB non injectée et import impossible")

# Vérifications
if not source_a_id or not source_b_id:
    raise Exception("IDs sources obligatoires")

utilisateur = session.get("user", "inconnu")

# ==============================
# DB HELPERS (ROBUSTES)
# ==============================
def get_source_info(source_id):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT nom_fichier, annee, mois
            FROM sources_clean
            WHERE id = %s
        """, (source_id,))
        row = cur.fetchone()

        if not row:
            raise Exception(f"Source introuvable : {source_id}")

        return row
    finally:
        cur.close()
        conn.close()


# ==============================
# FICHIERS
# ==============================
info_a = get_source_info(source_a_id)
info_b = get_source_info(source_b_id)

source_a_name = info_a["nom_fichier"]
source_b_name = info_b["nom_fichier"]

file_a = os.path.join(CLEAN_DIR, source_a_name)
file_b = os.path.join(CLEAN_DIR, source_b_name)

if not os.path.exists(file_a):
    raise FileNotFoundError(f"Fichier A introuvable : {file_a}")

if not os.path.exists(file_b):
    raise FileNotFoundError(f"Fichier B introuvable : {file_b}")

os.makedirs(SORTIE_DIR, exist_ok=True)

# ==============================
# LECTURE
# ==============================
df_a = pd.read_excel(file_a)
df_b = pd.read_excel(file_b)

df_a.columns = df_a.columns.str.strip()
df_b.columns = df_b.columns.str.strip()

if "NIU" not in df_a.columns or "NIU" not in df_b.columns:
    raise Exception("Colonne NIU obligatoire")

# ==============================
# JOINTURE
# ==============================
cols_b = [c for c in df_b.columns if c != "NIU"]
df = df_a.merge(df_b[["NIU"] + cols_b], on="NIU", how="left")

# ==============================
# CONTROLES
# ==============================
required_cols = ["Total général", "achats_hors_region_march"]

for col in required_cols:
    if col not in df.columns:
        raise Exception(f"Colonne manquante : {col}")

df["Total général"] = pd.to_numeric(df["Total général"], errors="coerce")
df["achats_hors_region_march"] = pd.to_numeric(df["achats_hors_region_march"], errors="coerce")

# ==============================
# TRAITEMENT
# ==============================
df = df[df["achats_hors_region_march"].notna()]
df = df[df["achats_hors_region_march"] != 0]

df["ecart"] = df["Total général"] - df["achats_hors_region_march"]
df = df[df["ecart"] >= 10_000_000]

df.sort_values(by="ecart", ascending=False, inplace=True)

# ==============================
# SORTIE
# ==============================
nom_fichier_sortie = f"matching_{source_a_id}X{source_b_id}_Valeurs_non_nulles_DSF.xlsx"
chemin_sortie = os.path.join(SORTIE_DIR, nom_fichier_sortie)

df.to_excel(chemin_sortie, index=False)

# ==============================
# FORMAT EXCEL
# ==============================
wb = load_workbook(chemin_sortie)
ws = wb.active

for col_name in ["Total général", "achats_hors_region_march", "ecart"]:
    if col_name in df.columns:
        col_index = df.columns.get_loc(col_name) + 1
        for row in range(2, ws.max_row + 1):
            ws.cell(row=row, column=col_index).number_format = '# ##0'

wb.save(chemin_sortie)

# ==============================
# RESULTAT
# ==============================
dernier_croisement = {
    "id_source_a": int(source_a_id),
    "id_source_b": int(source_b_id),
    "nom_fichier": nom_fichier_sortie,
    "type_fichier": "xlsx",
    "utilisateur": utilisateur,
    "date_stockage": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "nom_fichier_a": source_a_name,
    "nom_fichier_b": source_b_name
}

resultat_sortie = nom_fichier_sortie

print(f"✅ Fichier généré : {chemin_sortie}")

# \modules\analyse\templates\tableur_analyse.html
#-----------------------------------

<!DOCTYPE html>
<html lang="fr">

<head>
<meta charset="UTF-8">
<title>Tableur Analyse</title>

<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">

<link rel="stylesheet"
      href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
<link rel="stylesheet"
      href="https://cdn.datatables.net/buttons/2.4.1/css/buttons.dataTables.min.css">

<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.1/js/dataTables.buttons.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.1/js/buttons.html5.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.1/js/buttons.print.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/pdfmake.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/vfs_fonts.js"></script>

<style>
body {
    font-family: Arial;
    margin: 0;
    background: #f3f4f6;
}

/* Bannière */
.banniere-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    z-index: 10;
}
.banniere-container img {
    width: 100%;
    display: block;
    height: auto;
}

/* Sidebar */
.sidebar {
    position: fixed;
    left: 0;
    width: 110px;
    background-color: #1e293b;
    padding-top: 20px;
    overflow-y: auto;
    z-index: 9;
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

.sidebar a:hover {
    background-color: #0d5a72;
}

/* Contenu principal */
.main-content {
    margin-left: 110px;
    margin-top: 0; /* géré par JS */
    padding: 20px;
    overflow-x: auto;
}

/* h2 juste après bannière */
h2 {
    margin: 0;
    margin-bottom: 10px; /* espace avec le tableau */
    color: #1f2937;
    font-size: 1.2rem;
}

/* Tableau */
.table-container {
    margin: 0;
}

table.dataTable thead th {
    background: #2099b6;
    color: white;
}

table {
    border-collapse: collapse;
    min-width: 100%;
    width: max-content;
}

th, td {
    border: 1px solid #ccc;
    padding: 6px;
    font-size: 13px;
    white-space: nowrap;
    text-align: right;
}

th {
    background: #1e293b;
    color: white;
    text-align: center;
    position: sticky;
    top: 0;
    z-index: 2;
}

td:first-child,
th:first-child {
    text-align: left;
}

tr:nth-child(even) td {
    background: #f9f9f9;
}
</style>

</head>

<body>

<div class="banniere-container">
    <img src="{{ url_for('static', filename='images/tableau.jpg') }}">
</div>

<aside class="sidebar">
    <a href="/">Accueil</a>

    {% if modules.get("Ingestion") %}
    <a href="/ingestion">Ingestion</a>
    {% endif %}

    {% if modules.get("Apurement") %}
    <a href="/traitement/editor">Apurement</a>
    {% endif %}

    {% if modules.get("Croisement") %}
    <a href="/analyse">Croisement</a>
    {% endif %}

    {% if modules.get("Orientation") %}
    <a href="/exploitation">Orientation</a>
    {% endif %}

    {% if modules.get("Valorisation") %}
    <a href="/valorisation">Valorisation</a>
    {% endif %}

    {% if modules.get("Restitution") %}
    <a href="/notification">Restitution</a>
    {% endif %}

    <a href="{{ url_for('analyse.download_sortie', filename=filename) }}">Exporter</a>
</aside>

<main class="main-content">

    <!-- ✅ 1. h2 juste après bannière -->
    <h2>Fichier : {{ filename }}</h2>

    <!-- ✅ 2. tableau juste après h2 -->
    <div class="table-container">

        <table id="tableur" class="display nowrap" style="width:100%">
            <thead>
                <tr>
                    {% for col in columns %}
                    <th>{{ col }}</th>
                    {% endfor %}
                </tr>
            </thead>

            <tbody>
                {% for row in data %}
                <tr>
                    {% for col in columns %}
                        {% set val = row[col] %}
                        {% if val is number %}
                            <td>{{ "{:,.1f}".format(val)|replace(',', ' ') }}</td>
                        {% else %}
                            <td>{{ val }}</td>
                        {% endif %}
                    {% endfor %}
                </tr>
                {% endfor %}
            </tbody>
        </table>

    </div>

</main>

<script>
$(document).ready(function() {

    function ajusterLayout() {
        var bannerHeight = $('.banniere-container').outerHeight();

        $('.sidebar').css({
            top: bannerHeight + 'px',
            height: 'calc(100% - ' + bannerHeight + 'px)'
        });

        $('.main-content').css('margin-top', bannerHeight + 'px');
    }

    ajusterLayout();
    $(window).resize(ajusterLayout);

    $('#tableur').DataTable({
        scrollX: true,
        pageLength: 25,
        dom: 'Bfrtip',
        buttons: ['copy', 'excel', 'pdf']
    });
});
</script>

</body>
</html>