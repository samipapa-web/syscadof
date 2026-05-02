#
# MODULE 2: TRAITEMENT
#############################################################

# modules\traitement\templates\editor.html
#-------------------------------------------

<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Traitement des données – Éditeur de scripts</title>

<script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.15.0/ace.js"></script>

<style>
html, body {
    margin: 0;
    padding: 0;
    font-family: Arial,sans-serif;
    background: #f3f4f6;
}

/* BANNIERE */
.banniere-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    z-index: 1000;
}

.banniere-container img {
    width: 100%;
    height: auto;
    display: block;
}

:root { --banner-height:0px; }

/* SIDEBAR */
.sidebar {
    position: fixed;
    top: var(--banner-height);
    left: 0;
    bottom: 0;
    width: 110px;
    background: #1e293b;
    overflow-y: auto;
    padding-top: 10px;
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
    background: #127291;
    font-size: 12px;
}

.sidebar a:hover {
    background: #0d5a72;
}

/* CONTENU */
.main-content {
    margin-left: 110px;
    padding: 20px;
    padding-top: calc(20px + var(--banner-height));
    overflow-x: auto;
}

/* FORM */
label {
    font-weight: bold;
    display: block;
    margin-top: 15px;
}

select, input, button {
    width: 100%;
    padding: 6px;
    margin-top: 5px;
}

#editor {
    height: 400px;
    border: 1px solid #ccc;
    margin-top: 15px;
}

#log {
    margin-top: 15px;
    height: 40px;
    background: white;
    border: 1px solid #ccc;
    padding: 10px;
    overflow-y: auto;
    white-space: pre-wrap;
    font-size: 13px;
}

/* BUTTONS */
button {
    background: #2099b6;
    color: white;
    border: none;
    cursor: pointer;
    margin-top: 10px;
    border-radius: 4px;
}

button:hover {
    background: #127291;
}

/* TABLEAU */
table {
    border-collapse: collapse;
    width: 100%;
    margin-top: 10px;
}

table th, table td {
    border: 1px solid #ccc;
    padding: 5px;
    text-align: left;
}

table th {
    background: #127291;
    color: white;
}

/* BOUTON DOWNLOAD */
.btn-download {
    display: inline-block;
    padding: 4px 8px;
    background: #2099b6;
    color: white;
    text-decoration: none;
    border-radius: 4px;
    font-size: 12px;
}

.btn-download:hover {
    background: #127291;
}
</style>
</head>
<body>

<div class="banniere-container">
    <img src="{{ url_for('static', filename='images/traitement.jpg') }}">
</div>

<aside class="sidebar">
    <a href="/">Accueil</a>
    {% if modules.get("Ingestion") %}<a href="/ingestion">Ingestion</a>{% endif %}
    {% if modules.get("Apurement") %}<a href="/traitement/editor">Apurement</a>{% endif %}
    {% if modules.get("Croisement") %}<a href="/analyse">Croisement</a>{% endif %}
    {% if modules.get("Orientation") %}<a href="/exploitation">Orientation</a>{% endif %}
    {% if modules.get("Valorisation") %}<a href="/valorisation">Valorisation</a>{% endif %}
    {% if modules.get("Restitution") %}<a href="/notification">Restitution</a>{% endif %}
</aside>

<main class="main-content">
    <label>Source de données</label>
    <select id="sourceLacSelect"></select>

    <label>Script de traitement</label>
    <select id="scriptSelect"></select>

    <button id="loadScriptBtn">Charger le script</button>
    <div id="editor"># Le script apparaîtra ici</div>

    <label>Titre du nouveau script</label>
    <input id="newScriptTitle">

    <button id="saveScriptBtn">Sauvegarder comme nouveau script</button>
    <button id="runScriptBtn">Exécuter le script</button>

    <div id="log">Chargement en cours...</div>

    <h2>Historique des sources apurées</h2>
    <table>
        <thead>
            <tr>
                <th>ID</th><th>Source</th><th>Fournisseur</th><th>Temporalite</th>
                <th>Année</th><th>Mois</th><th>Type</th><th>Utilisateur</th><th>Date</th><th>Statut</th>
            </tr>
        </thead>
        <tbody id="historiqueBody"></tbody>
    </table>
</main>

<script>
const editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.session.setMode("ace/mode/python");

const log = document.getElementById("log");
const sourceLacSelect = document.getElementById("sourceLacSelect");
const scriptSelect = document.getElementById("scriptSelect");
const newScriptTitle = document.getElementById("newScriptTitle");
const historiqueBody = document.getElementById("historiqueBody");

function writeLog(msg){ log.textContent = msg; }

function adjustLayout(){
    const banner=document.querySelector(".banniere-container img");
    if(banner){
        const height=banner.offsetHeight+"px";
        document.documentElement.style.setProperty("--banner-height",height);
    }
}
window.addEventListener("load", adjustLayout);
window.addEventListener("resize", adjustLayout);

// =========================
// LOAD SOURCES
// =========================
async function loadSourcesLac(){
    writeLog("Chargement des sources...");
    try{
        const res = await fetch("/traitement/api/sources-lac");
        if(!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        sourceLacSelect.innerHTML = "";
        if(!data.length) writeLog("Aucune source trouvée.");
        else writeLog(`${data.length} sources chargées.`);
        data.forEach(x=>{
            const o=document.createElement("option");
            o.value = x.id;
            o.textContent = `${x.intitule_source} (${x.annee}/${x.mois || '-'})`;
            sourceLacSelect.appendChild(o);
        });
    }catch(err){
        writeLog("Erreur sources : "+err.message);
        console.error(err);
    }
}

// =========================
// LOAD SCRIPTS
// =========================
async function loadScripts(){
    writeLog("Chargement des scripts...");
    try{
        const res = await fetch("/traitement/api/scripts");
        if(!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        scriptSelect.innerHTML = "";
        if(!data.length) writeLog("Aucun script trouvé.");
        else writeLog(`${data.length} scripts chargés.`);
        data.forEach(x=>{
            const o=document.createElement("option");
            o.value = x.id;
            o.textContent = `${x.titre}`;
            scriptSelect.appendChild(o);
        });
    }catch(err){
        writeLog("Erreur scripts : "+err.message);
        console.error(err);
    }
}

// =========================
// LOAD HISTORIQUE
// =========================
async function loadHistoriqueSources(){
    writeLog("Chargement historique...");
    try{
        const res = await fetch("/traitement/api/historique-sources-apurees");
        if(!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        historiqueBody.innerHTML="";
        data.forEach(row=>{
            const tr = document.createElement("tr");
            const filePath = encodeURIComponent(row.nom_fichier);
            tr.innerHTML=`
                <td>${row.source_id}</td>
                <td>${row.intitule_source}</td>
                <td>${row.fournisseur}</td>
                <td>${row.temporalite}</td>
                <td>${row.annee}</td>
                <td>${row.mois}</td>
                <td><a href="/traitement/tableur/${filePath}" target="_blank" class="btn-download">${row.type_fichier}</a></td>
                <td>${row.utilisateur}</td>
                <td>${row.date_apurement}</td>
                <td>${row.statut}</td>
            `;
            historiqueBody.appendChild(tr);
        });
        writeLog(`${data.length} lignes dans l'historique.`);
    }catch(err){
        writeLog("Erreur historique : "+err.message);
        console.error(err);
    }
}

// =========================
// LOAD SCRIPT ON CLICK
// =========================
document.getElementById("loadScriptBtn").onclick = async ()=>{
    if(!scriptSelect.value) return writeLog("Sélectionnez un script.");
    try{
        const res = await fetch(`/traitement/api/get-script/${scriptSelect.value}`);
        if(!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if(data.success){
            editor.setValue(data.contenu,-1);
            writeLog("Script chargé.");
        } else writeLog("Erreur : "+data.error);
    }catch(err){
        writeLog("Erreur chargement script : "+err.message);
        console.error(err);
    }
}

// =========================
// RUN SCRIPT
// =========================
document.getElementById("runScriptBtn").onclick = async ()=>{
    if(!sourceLacSelect.value) return writeLog("Sélectionnez une source.");
    if(!scriptSelect.value) return writeLog("Sélectionnez un script.");
    const f = new FormData();
    f.append("source_lac_id", sourceLacSelect.value);
    f.append("script_contenu", editor.getValue());
    writeLog("Exécution...");
    try{
        const res = await fetch(`/traitement/api/run-script/${scriptSelect.value}`,{method:"POST", body:f});
        if(!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if(data.success) writeLog(data.message);
        else writeLog("Erreur : "+data.error);
    }catch(err){
        writeLog("Erreur exécution : "+err.message);
        console.error(err);
    }
    loadHistoriqueSources();
}

// =========================
// INITIALIZE
// =========================
window.addEventListener("load", ()=>{
    loadSourcesLac();
    loadScripts();
    loadHistoriqueSources();
});
</script>

</body>
</html>


#
# modules\traitement\templates\tableur.html
# --------------------------------------------

<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Fichier - {{ filename }}</title>

<!-- DataTables CSS -->
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
<link rel="stylesheet" href="https://cdn.datatables.net/buttons/2.4.1/css/buttons.dataTables.min.css">

<!-- jQuery + DataTables JS -->
<script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.1/js/dataTables.buttons.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.1/js/buttons.html5.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.1/js/buttons.print.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/pdfmake.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/vfs_fonts.js"></script>

<style>
body {
    font-family: Arial, sans-serif;
    margin: 0;
    background: #f3f4f6;
}

/* =========================
BANNIÈRE
========================= */
.banniere-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    z-index: 10;
}
.banniere-container img {
    width: 100%;
    height: auto;
    display: block;
}

/* =========================
SIDEBAR
========================= */
.sidebar {
    position: fixed;
    left: 0;
    width: 110px;
    background-color: #1e293b;
    padding-top: 20px;
    overflow-y: auto;
    z-index: 9;
}

/* =========================
CONTENU PRINCIPAL
========================= */
.main-content {
    margin-left: 110px;
    padding: 20px;
    overflow-x: auto;
    margin-top: 0; /* ajusté dynamiquement */
}

/* =========================
SIDEBAR LINKS
========================= */
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

/* =========================
TITRE
========================= */
h2 {
    margin: 0 0 10px 0;
    color: #1f2937;
    font-size: 1.2rem;
}

/* =========================
TABLEAU
========================= */
table.dataTable thead th {
    background: #2099b6;
    color: white;
    max-width: 10vw;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
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
    max-width: 10vw;
    overflow: hidden;
    text-overflow: ellipsis;
}
th {
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

<!-- =========================
BANNIÈRE
========================= -->
<div class="banniere-container">
    <img id="banniere-img" src="{{ url_for('static', filename='images/tableau.jpg') }}">
</div>

<!-- =========================
SIDEBAR
========================= -->
<aside class="sidebar">
    <a href="/">Accueil</a>
    {% if modules.get("Ingestion") %}<a href="/ingestion">Ingestion</a>{% endif %}
    {% if modules.get("Apurement") %}<a href="/traitement/editor">Apurement</a>{% endif %}
    {% if modules.get("Croisement") %}<a href="/analyse">Croisement</a>{% endif %}
    {% if modules.get("Orientation") %}<a href="/exploitation">Orientation</a>{% endif %}
    {% if modules.get("Valorisation") %}<a href="/valorisation">Valorisation</a>{% endif %}
    {% if modules.get("Restitution") %}<a href="/notification">Restitution</a>{% endif %}
    <a href="{{ url_for('traitement.download_sortie', filename=filename) }}">Exporter</a>
</aside>

<!-- =========================
CONTENU PRINCIPAL
========================= -->
<main class="main-content">
    <h2>Fichier : {{ filename }}</h2>
    <div class="table-container">
        <table id="tableur" class="display nowrap" style="width:100%">
            <thead>
                <tr>
                    {% for col in columns %}
                    <th>{{ col | replace("'", "\\'") }}</th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    </div>
</main>

<!-- =========================
SCRIPT
========================= -->
<script>
$(document).ready(function() {

    function ajusterLayout() {
        let bannerHeight = $('#banniere-img').outerHeight();

        $('.sidebar').css({
            top: bannerHeight + 'px',
            height: 'calc(100% - ' + bannerHeight + 'px)'
        });

        $('.main-content').css('margin-top', bannerHeight + 'px');
    }

    $('#banniere-img').on('load', ajusterLayout);
    $(window).resize(ajusterLayout);
    if ($('#banniere-img')[0].complete) { ajusterLayout(); }

    $('#tableur').DataTable({
        processing: true,
        serverSide: true,
        ajax: {
            url: "/traitement/api/tableur-data/{{ filename }}",
            type: "GET"
        },
        pageLength: 100,
        lengthMenu: [[100, 200, 500], [100, 200, 500]],
        language: { url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/fr-FR.json" },
        scrollX: true,
        autoWidth: false,
        dom: 'Bfrtip',
        buttons: ['copy', 'excel', 'pdf'],

        columns: [
            {% for col in columns %}
            { data: "{{ col | replace("'", "\\'") }}" }{% if not loop.last %},{% endif %}
            {% endfor %}
        ],

        // =========================
        // Formatage et alignement
        // =========================
        columnDefs: [
            {
                targets: '_all',
                createdCell: function(td, cellData) {
                    if (!isNaN(cellData) && cellData !== null && cellData !== '') {
                        $(td).text(Number(cellData).toLocaleString('fr-FR', { maximumFractionDigits: 2 }));
                        $(td).css('text-align', 'right');
                    } else {
                        $(td).css('text-align', 'left');
                    }
                }
            }
        ],

        createdRow: function(row, data) {
            $('td', row).each(function() {
                $(this).attr('title', $(this).text());
            });
        }
    });
});
</script>

</body>
</html>


# modules/traitement/routes.py
#------------------------------------------------------------------------------

from flask import Blueprint, jsonify, request, render_template, send_from_directory, abort, current_app
import os
from datetime import datetime
import pandas as pd
from werkzeug.utils import secure_filename

# Service script
from modules.traitement.services import execute_script

traitement_bp = Blueprint(
    "traitement",
    __name__,
    url_prefix="/traitement",
    template_folder="templates"
)

# =========================
# PostgreSQL - Connexion sécurisée
# =========================
def get_pg_connection():
    """
    Retourne une connexion PostgreSQL depuis la config Flask.
    """
    from flask import current_app
    BASE_DIR = current_app.config["BASE_DIR"]

    import sys
    if BASE_DIR not in sys.path:
        sys.path.append(BASE_DIR)

    from database import get_connection
    return get_connection()


# =========================
# PAGE
# =========================
@traitement_bp.route("/editor")
def editor():
    return render_template("editor.html")


# =========================
# SOURCES LAC (debug)
# =========================
@traitement_bp.route("/api/sources-lac")
def list_sources_lac():
    try:
        with get_pg_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, intitule_source, annee, mois, nom_fichier
                    FROM sources_lac
                    ORDER BY date_stockage DESC
                """)
                rows = cur.fetchall()

        # Debug : afficher dans le log ce qui est récupéré
        current_app.logger.info(f"[DEBUG] sources_lac rows: {rows}")
        print("[DEBUG] sources_lac rows:", rows)

        return jsonify(rows)
    except Exception as e:
        current_app.logger.error(f"ERREUR sources-lac: {e}")
        print("ERREUR sources-lac:", e)
        return jsonify([])




# =========================
# HISTORIQUE
# =========================
@traitement_bp.route("/api/historique-sources-apurees")
def historique_sources_apurees():
    try:
        with get_pg_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT source_id, intitule_source, categorie, fournisseur, temporalite,
                           annee, mois, type_fichier, nom_fichier,
                           utilisateur, date_apurement, statut
                    FROM sources_clean
                    ORDER BY date_apurement DESC NULLS LAST
                """)
                return jsonify(cur.fetchall())
    except Exception as e:
        current_app.logger.error(f"ERREUR historique: {e}")
        return jsonify([])


# =========================
# SCRIPTS (debug)
# =========================
@traitement_bp.route("/api/scripts")
def list_scripts():
    try:
        with get_pg_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, titre, auteur
                    FROM base_scripts
                    ORDER BY date_stockage DESC
                """)
                rows = cur.fetchall()

        # Debug : afficher dans le log ce qui est récupéré
        current_app.logger.info(f"[DEBUG] base_scripts rows: {rows}")
        print("[DEBUG] base_scripts rows:", rows)

        return jsonify(rows)
    except Exception as e:
        current_app.logger.error(f"ERREUR scripts: {e}")
        print("ERREUR scripts:", e)
        return jsonify([])


# =========================
# GET SCRIPT
# =========================
@traitement_bp.route("/api/get-script/<int:script_id>")
def get_script(script_id):
    try:
        with get_pg_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT chemin_script FROM base_scripts WHERE id=%s", (script_id,))
                row = cur.fetchone()

        if not row:
            return jsonify({"success": False, "error": "Script introuvable"})

        chemin = row["chemin_script"]

        if not os.path.exists(chemin):
            return jsonify({"success": False, "error": "Fichier absent"})

        with open(chemin, "r", encoding="utf-8") as f:
            contenu = f.read()

        return jsonify({"success": True, "contenu": contenu})

    except Exception as e:
        current_app.logger.error(f"ERREUR get-script: {e}")
        return jsonify({"success": False, "error": str(e)})


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

        with get_pg_connection() as conn:
            with conn.cursor() as cur:

                # Récupération script
                cur.execute("SELECT chemin_script FROM base_scripts WHERE id=%s", (script_id,))
                script = cur.fetchone()
                if not script:
                    raise Exception("Script introuvable")
                chemin_script = script["chemin_script"]

                # Récupération source
                cur.execute("SELECT * FROM sources_lac WHERE id=%s", (source_lac_id,))
                source = cur.fetchone()
                if not source:
                    raise Exception("Source introuvable")

                # Exécution du script
                output = execute_script(chemin_script, source_lac_id, BASE_DIR)
                parts = output.split("||")
                if len(parts) != 2:
                    raise Exception("Format de sortie du script invalide")
                chemin_clean, nom_clean = parts

                # Insertion dans sources_clean
                cur.execute("""
                    INSERT INTO sources_clean (
                        source_id, intitule_source, categorie, fournisseur, temporalite,
                        annee, mois, type_fichier, chemin, nom_fichier,
                        utilisateur, date_apurement, statut
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    source["id"],
                    source["intitule_source"],
                    source.get("categorie", "Non définie"),
                    source["fournisseur"],
                    source["temporalite"],
                    source["annee"],
                    source["mois"],
                    source["type_fichier"],
                    chemin_clean,
                    nom_clean,
                    source["utilisateur"],
                    datetime.now(),
                    "Succès"
                ))

        return jsonify({"success": True, "message": "Script exécuté avec succès"})

    except Exception as e:
        current_app.logger.error(f"ERREUR run-script: {e}")
        return jsonify({"success": False, "error": str(e)})


# =========================
# TABLEUR
# =========================
@traitement_bp.route("/tableur/<filename>")
def view_tableur(filename):
    CLEAN_DIR = current_app.config["DATA_CLEAN_DIR"]
    safe = secure_filename(filename)
    file_path = os.path.join(CLEAN_DIR, safe)

    if not os.path.exists(file_path):
        abort(404)

    df = pd.read_csv(file_path, nrows=1) if filename.endswith(".csv") else pd.read_excel(file_path, nrows=1)
    return render_template("tableur.html", filename=filename, columns=df.columns)


# =========================
# DATA TABLEUR
# =========================
@traitement_bp.route("/api/tableur-data/<filename>")
def tableur_data(filename):
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


# =========================
# DOWNLOAD
# =========================
@traitement_bp.route("/download/<path:filename>")
def download_sortie(filename):
    CLEAN_DIR = current_app.config["DATA_CLEAN_DIR"]
    safe = secure_filename(filename)
    return send_from_directory(CLEAN_DIR, safe, as_attachment=True)
    
    

    

# modules/traitement/services.py
#--------------------------------------------------------

import subprocess
import sys
import os


def execute_script(chemin_script, source_lac_id, base_dir):
    """
    Exécute un script Python externe (subprocess)
    avec injection de BASE_DIR et source_lac_id
    """

    if not os.path.exists(chemin_script):
        raise FileNotFoundError("Script introuvable")

    result = subprocess.run(
        [sys.executable, chemin_script],
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "source_lac_id": str(source_lac_id),
            "BASE_DIR": base_dir  # 🔥 injection critique
        }
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return result.stdout.strip()
    

# modules\traitement\insert_scripts.py

import os
from datetime import datetime
from flask import current_app
from modules.traitement.routes import get_pg_connection  # connexion centralisée

# ===============================
# SYNCHRONISATION (RESET + INSERT)
# ===============================
def sync_scripts_to_db(app=None):
    """
    Réinitialise et insère tous les scripts Python du dossier SCRIPTS_FOLDER
    dans la table base_scripts. 
    - app : instance Flask pour récupérer config si appelée en dehors du contexte request.
    """

    # ⚡ Récupérer la config depuis l'app si fournie, sinon current_app
    cfg = app.config if app else current_app.config

    BASE_DIR = cfg.get("BASE_DIR")
    SCRIPTS_FOLDER = cfg.get("APUR_SCRIPT_DIR")

    if not os.path.exists(SCRIPTS_FOLDER):
        raise FileNotFoundError(f"Dossier scripts introuvable : {SCRIPTS_FOLDER}")

    # Connexion PostgreSQL centralisée
    conn = get_pg_connection()
    cur = conn.cursor()

    now = datetime.now()

    try:
        # 1️⃣ Suppression totale
        cur.execute("DELETE FROM base_scripts")
        conn.commit()

        # Reset auto-increment (séquence)
        cur.execute("ALTER SEQUENCE base_scripts_id_seq RESTART WITH 1")
        conn.commit()

        # 2️⃣ Réinsertion des scripts
        script_files = [f for f in os.listdir(SCRIPTS_FOLDER) if f.endswith(".py")]

        for f in script_files:
            chemin_script = os.path.join(SCRIPTS_FOLDER, f)
            titre = os.path.splitext(f)[0]

            cur.execute("""
                INSERT INTO base_scripts (titre, object, auteur, chemin_script, date_stockage)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                titre,
                "Traitement",
                ".",
                chemin_script,
                now
            ))

        conn.commit()

        print(f"[SYNC] {len(script_files)} script(s) réinitialisé(s)")

    except Exception as e:
        conn.rollback()
        print(f"[SYNC ERROR] {e}")

    finally:
        cur.close()
        conn.close()
        
        
 
 #modules\traitement\scripts\script_traitement.py
 #---------------------------------------------------
import os
import shutil
import sys

# =========================
# BASE_DIR depuis Flask
# =========================
BASE_DIR = os.environ.get("BASE_DIR")

if not BASE_DIR:
    print("Erreur : BASE_DIR non défini", file=sys.stderr)
    sys.exit(1)

# permettre import database
sys.path.append(BASE_DIR)

from database import get_connection


# =========================
# INPUT
# =========================
source_lac_id = int(os.environ.get("source_lac_id", 0))

if not source_lac_id:
    print("Erreur : source_lac_id non défini", file=sys.stderr)
    sys.exit(1)


# =========================
# DB
# =========================
conn = get_connection()
cur = conn.cursor()

cur.execute("SELECT * FROM sources_lac WHERE id=%s", (source_lac_id,))
source = cur.fetchone()

if not source:
    print("Source introuvable", file=sys.stderr)
    sys.exit(1)


# =========================
# CHEMINS
# =========================
LAC_DIR = os.path.join(BASE_DIR, "data", "lac")   # ⚠️ cohérent avec app.py
CLEAN_DIR = os.path.join(BASE_DIR, "data", "clean")

os.makedirs(CLEAN_DIR, exist_ok=True)

nom_fichier = source["nom_fichier"]
annee = source["annee"]
mois = source["mois"]

chemin_source = os.path.join(LAC_DIR, nom_fichier)

if not os.path.exists(chemin_source):
    print(f"Fichier source introuvable : {chemin_source}", file=sys.stderr)
    sys.exit(1)


nom_clean = f"clean_{annee}_{mois}_{nom_fichier}"
chemin_clean = os.path.join(CLEAN_DIR, nom_clean)


# =========================
# Copier
# =========================
shutil.copy2(chemin_source, chemin_clean)

# -----------------------------
# Traitement fichier Excel/CSV
# -----------------------------

#aucun traitement

cur.close()
conn.close()


# =========================
# OUTPUT
# =========================
print(f"{chemin_clean}||{nom_clean}")

.
#Le bouton "Executer le script" de la page traitement.html lance l'execution de script_traitement.py