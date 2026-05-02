
## MODULE 1: INGESTION
## -----------------------------------------------

# \modules\ingestion\templates\ingestion.html
#-----------------------------------

<!DOCTYPE html>
<html lang="fr">

<head>
<meta charset="UTF-8">
<title>SYSCADOF - Ingestion</title>

<style>
html, body { margin:0; padding:0; font-family: Arial,sans-serif; background:#f3f4f6; }
.banniere-container { position: fixed; top:0; left:0; width:100%; z-index:1000; }
.banniere-container img { width:100%; height:auto; display:block; }
:root { --banner-height: 0px; }

.sidebar {
    position: fixed;
    top: var(--banner-height);
    left: 0;
    bottom: 0;
    width: 110px;
    background-color: #1e293b;
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
    background-color: #127291;
    font-size: 12px;
}
.sidebar a:hover { background-color: #0d5a72; }

.main-content {
    margin-left: 110px;
    padding: 20px;
    padding-top: calc(20px + var(--banner-height));
    overflow-x: auto;
}
h1 { color:#2099b6; }
h2 { color:#1f2937; margin-top:30px; }
label { font-weight:bold; }

select, input[type="number"], input[type="file"] {
    width:100%;
    padding:6px;
    margin:5px 0;
    border:1px solid #ccc;
    border-radius:4px;
    box-sizing:border-box;
}
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

.form-grid { display:flex; flex-direction:column; gap:12px; margin-top:15px; margin-bottom:15px; }
.form-row { display:grid; grid-template-columns:230px 1fr; align-items:center; gap:15px; }

table {
    width:100%;
    border-collapse: collapse;
    margin-top:20px;
    background:white;
}
th { background:#2099b6; color:white; padding:10px; text-align:center; }
td { padding:8px; border-bottom:1px solid #ddd; text-align:left; }
.separator { border:none; border-top:2px solid #2099b6; margin:40px 0 10px 0; }
.open-btn {
    display:inline-block;
    padding:4px 8px;
    background-color:#2099b6;
    color:white;
    border-radius:4px;
    text-decoration:none;
    font-size:0.9rem;
}
.open-btn:hover { background-color:#167d94; }
#message { margin-top:10px; font-weight:bold; color:red; }

</style>
</head>

<body>

<div class="banniere-container">
    <img src="{{ url_for('static', filename='images/ingestion.jpg') }}" alt="Ingestion">
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
<h1>INGESTION DES SOURCES DE DONNÉES</h1>

<div class="form-grid">
<form id="form-ingestion">
    <div class="form-row">
        <label for="fournisseur">Fournisseur</label>
        <select id="fournisseur" required>
            <option value="">-- Sélectionner --</option>
            {% for f in fournisseurs %}
            <option value="{{ f }}">{{ f }}</option>
            {% endfor %}
        </select>
    </div>

    <div class="form-row">
        <label for="source_id">Intitulé de la source</label>
        <select id="source_id" name="source_id" required></select>
    </div>

    <div class="form-row">
        <label for="annee">Année</label>
        <input type="number" id="annee" name="annee" min="2000" max="2100" required>
    </div>

    <div class="form-row">
        <label for="mois">Mois (optionnel)</label>
        <select id="mois" name="mois">
            <option value="">--</option>
            {% for m,v in [(1,'Janvier'),(2,'Février'),(3,'Mars'),(4,'Avril'),(5,'Mai'),(6,'Juin'),
                          (7,'Juillet'),(8,'Août'),(9,'Septembre'),(10,'Octobre'),(11,'Novembre'),(12,'Décembre')] %}
            <option value="{{ m }}">{{ v }}</option>
            {% endfor %}
        </select>
    </div>

    <div class="form-row">
        <label for="file">Fichier</label>
        <input type="file" id="file" name="file" required>
    </div>

    <div class="form-row">
        <button type="submit">Uploader</button>
    </div>
</form>
</div>

<div id="message"></div>

<hr class="separator">

<h2>Historique des sources stockées</h2>
<table>
<thead>
<tr>
<th>ID</th>
<th>Intitulé source</th>
<th>Fournisseur</th>
<th>Temporalité</th>
<th>Année</th>
<th>Mois</th>
<th>Type</th>
<th>Utilisateur</th>
<th>Date stockage</th>
</tr>
</thead>
<tbody>
{% if sources %}
{% for s in sources %}
<tr>
<td>{{ s.id }}</td>
<td>{{ s.intitule_source }}</td>
<td>{{ s.fournisseur }}</td>
<td>{{ s.temporalite }}</td>
<td>{{ s.annee }}</td>
<td>{{ s.mois }}</td>
<td>
<a href="{{ url_for('ingestion.download_lac', id=s.id) }}" class="open-btn">{{ s.type_fichier }}</a>
</td>
<td>{{ s.utilisateur }}</td>
<td>{{ s.date_stockage }}</td>
</tr>
{% endfor %}
{% else %}
<tr><td colspan="9">Aucune source enregistrée</td></tr>
{% endif %}
</tbody>
</table>
</main>

<script>
function adjustLayout() {
    const banner = document.querySelector(".banniere-container img");
    if(banner){
        document.documentElement.style.setProperty("--banner-height", banner.offsetHeight + "px");
    }
}
window.addEventListener("load", adjustLayout);
window.addEventListener("resize", adjustLayout);

document.addEventListener("DOMContentLoaded", () => {
    const fournisseurSelect = document.getElementById("fournisseur");
    const sourceSelect = document.getElementById("source_id");
    const formIngestion = document.getElementById("form-ingestion");
    const messageDiv = document.getElementById("message");

    fournisseurSelect.addEventListener("change", () => {
        const fournisseur = fournisseurSelect.value;
        sourceSelect.innerHTML = "";
        if (!fournisseur) return;

        fetch(`/ingestion/api/get-sources/${encodeURIComponent(fournisseur)}`)
            .then(res => res.json())
            .then(data => {
                if (data.sources.length > 0) {
                    data.sources.forEach(src => {
                        const opt = document.createElement("option");
                        opt.value = src.id;
                        opt.textContent = src.intitule_source;
                        sourceSelect.appendChild(opt);
                    });
                    formIngestion.style.display = "block";
                } else {
                    sourceSelect.innerHTML = "<option value=''>Aucune source disponible</option>";
                    formIngestion.style.display = "none";
                }
            })
            .catch(err => {
                console.error(err);
                messageDiv.textContent = "Erreur lors du chargement des sources.";
            });
    });

    formIngestion.addEventListener("submit", (e) => {
        e.preventDefault();
        messageDiv.textContent = "";

        const formData = new FormData(formIngestion);
        formData.append("fournisseur", fournisseurSelect.value);

        fetch("/ingestion/api/upload", { method:"POST", body:formData })
        .then(res => res.json())
        .then(data => {
            messageDiv.style.color = data.success ? "green" : "red";
            messageDiv.textContent = data.message;
            if(data.success) setTimeout(()=>location.reload(), 1000);
        })
        .catch(err => {
            console.error(err);
            messageDiv.style.color = "red";
            messageDiv.textContent = "Erreur lors de l'upload du fichier.";
        });
    });
});
</script>

</body>
</html>

# \modules\ingestion\models.py
#-----------------------------------

# modules/ingestion/models.py

from database import get_connection

def init_db():
    """
    Initialise les tables pour PostgreSQL.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Table sources
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sources (
            id SERIAL PRIMARY KEY,
            intitule TEXT NOT NULL,
            provenance TEXT,
            fournisseur TEXT,
            categorie TEXT,
            temporalite TEXT
        )
    """)

    # Table fichiers
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fichiers (
            id SERIAL PRIMARY KEY,
            source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE,
            annee INTEGER,
            mois INTEGER,
            type_fichier TEXT,
            date_stockage TIMESTAMP,
            stockeur TEXT,
            chemin TEXT
        )
    """)

    # Table sources_lac (historique LAC)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sources_lac (
            id SERIAL PRIMARY KEY,
            source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE,
            intitule_source TEXT,
            provenance TEXT,
            fournisseur TEXT,
            categorie TEXT,
            temporalite TEXT,
            annee INTEGER,
            mois INTEGER,
            type_fichier TEXT,
            chemin TEXT,
            nom_fichier TEXT,
            taille BIGINT,
            hash_fichier TEXT,
            utilisateur TEXT,
            date_stockage TIMESTAMP
        )
    """)

    # Table sources_clean (copie pour nettoyage)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sources_clean (
            id SERIAL PRIMARY KEY,
            source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE,
            intitule_source TEXT,
            provenance TEXT,
            fournisseur TEXT,
            categorie TEXT,
            temporalite TEXT,
            annee INTEGER,
            mois INTEGER,
            type_fichier TEXT,
            chemin TEXT,
            nom_fichier TEXT,
            taille BIGINT,
            hash_fichier TEXT,
            utilisateur TEXT,
            date_stockage TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


# \modules\ingestion\routes.py
#-----------------------------------

# modules/ingestion/routes.py
#-----------------------------------

import os
from flask import Blueprint, render_template, request, send_from_directory, session, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
from psycopg2.extras import RealDictCursor
from database import get_connection

UPLOAD_FOLDER = "data/LAC"
ALLOWED_EXTENSIONS = {"csv", "xlsx", "txt"}

ingestion_bp = Blueprint(
    "ingestion",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/ingestion"
)

# -----------------------------
# Vérification extension fichier
# -----------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# -----------------------------
# Page principale
# -----------------------------
@ingestion_bp.route("/")
def page_ingestion():
    utilisateur = session.get("user", "inconnu")
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Historique des fichiers LAC
        cur.execute("SELECT * FROM sources_lac ORDER BY id DESC")
        sources = cur.fetchall()

        # Fournisseurs actifs
        cur.execute("""
            SELECT DISTINCT fournisseur
            FROM sources_donnees
            WHERE fournisseur IS NOT NULL
            ORDER BY fournisseur
        """)
        fournisseurs = [row['fournisseur'] for row in cur.fetchall()]

    finally:
        cur.close()
        conn.close()

    return render_template(
        "ingestion.html",
        sources=sources,
        fournisseurs=fournisseurs,
        current_user=utilisateur
    )

# -----------------------------
# API : récupérer sources par fournisseur
# -----------------------------
@ingestion_bp.route("/api/get-sources/<fournisseur>")
def get_sources(fournisseur):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Comparaison insensible à la casse et suppression espaces superflus
        cur.execute("""
            SELECT id, intitule_source AS intitule_source
            FROM sources_donnees
            WHERE TRIM(LOWER(fournisseur)) = TRIM(LOWER(%s))
            ORDER BY intitule_source
        """, (fournisseur.strip(),))

        sources = [{"id": row['id'], "intitule_source": row['intitule_source']} for row in cur.fetchall()]
    finally:
        cur.close()
        conn.close()

    return jsonify({"sources": sources})

# -----------------------------
# Upload fichier
# -----------------------------
@ingestion_bp.route("/api/upload", methods=["POST"])
def upload_file():
    utilisateur = session.get("user", "inconnu")

    fournisseur = request.form.get("fournisseur")
    source_id = request.form.get("source_id")
    annee = request.form.get("annee")
    mois = request.form.get("mois") or 0
    file = request.files.get("file")

    if not file or not allowed_file(file.filename):
        return jsonify({"success": False, "message": "Fichier non autorisé"})

    filename = secure_filename(file.filename)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    taille = os.path.getsize(filepath)
    extension = filename.rsplit(".", 1)[1].lower()
    date_stockage = datetime.now()

    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Récupérer infos source
        cur.execute("SELECT * FROM sources_donnees WHERE id=%s", (source_id,))
        src = cur.fetchone()
        if not src:
            return jsonify({"success": False, "message": "Source invalide"})

        # Insertion dans sources_lac
        cur.execute("""
            INSERT INTO sources_lac
            (source_id, intitule_source, provenance, fournisseur, categorie,
             temporalite, annee, mois, type_fichier, chemin, nom_fichier,
             taille, hash_fichier, utilisateur, date_stockage)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            src['id'], src['intitule_source'], src['provenance'], src['fournisseur'], src['categorie'], src['temporalite'],
            annee, mois, extension, UPLOAD_FOLDER, filename,
            taille, None, utilisateur, date_stockage
        ))

        # Copie CLEAN
        os.makedirs("data/clean", exist_ok=True)
        cur.execute("""
            INSERT INTO sources_clean
            (source_id, intitule_source, provenance, fournisseur, categorie,
             temporalite, annee, mois, type_fichier, chemin, nom_fichier,
             taille, hash_fichier, utilisateur, date_stockage)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            src['id'], src['intitule_source'], src['provenance'], src['fournisseur'], src['categorie'], src['temporalite'],
            annee, mois, extension, "data/clean", filename,
            taille, None, utilisateur, date_stockage
        ))

        conn.commit()
    finally:
        cur.close()
        conn.close()

    return jsonify({"success": True, "message": "Fichier uploadé avec succès"})

# -----------------------------
# Télécharger fichier LAC
# -----------------------------
@ingestion_bp.route("/download/<int:id>")
def download_lac(id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("SELECT chemin, nom_fichier FROM sources_lac WHERE id=%s", (id,))
        row = cur.fetchone()
    finally:
        cur.close()
        conn.close()

    if row:
        return send_from_directory(row['chemin'], row['nom_fichier'], as_attachment=True)
    return "Fichier introuvable", 404

# \modules\ingestion\services.py
#-----------------------------------

import os, datetime
from werkzeug.utils import secure_filename
from database import get_connection
from config import LAC_DIR, ALLOWED_EXTENSIONS

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, source_id, annee, mois, stockeur):
    ext = file.filename.rsplit(".", 1)[1].lower()
    fname = secure_filename(f"{source_id}_{annee}_{mois}_{datetime.datetime.now().timestamp()}.{ext}")
    path = os.path.join(LAC_DIR, fname)
    os.makedirs(LAC_DIR, exist_ok=True)
    file.save(path)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO fichiers(source_id, annee, mois, type_fichier, date_stockage, stockeur, chemin)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (source_id, annee, mois, ext, datetime.datetime.now(), stockeur, path))
    conn.commit()
    cur.close()
    conn.close()


# \static\css\style.css
#-----------------------------------------------

/* ============================
   Styles généraux
   ============================ */
body {
    font-family: Arial, sans-serif;
    background-color: #f3f4f6;
    margin: 0;
    padding: 0;
    color: #333;
}

.page-container {
    display: flex;
    min-height: 100vh;
}

/* ============================
   Sidebar gauche
   ============================ */
.sidebar.left {
    width: 200px;
    background-color: #1e293b;
}

/* ============================
   Contenu principal
   ============================ */
.content {
    flex: 1;
    padding: 30px;
}

/* Titres */
h1 {
    color: #2099b6;
    font-size: 1.7rem;
    margin-top: 0;
}

h2 {
    color: #1f2937;
    margin-top: 30px;
    font-size: 1.2rem;
}

/* Sous-titres */
.form-subtitle {
    color: #555;
    margin-bottom: 20px;
}

/* ============================
   Formulaires
   ============================ */
form label {
    display: block;
    margin-top: 15px;
    font-weight: bold;
}

form input[type="number"],
form select,
form input[type="file"] {
    width: 100%;
    padding: 8px 10px;
    margin-top: 5px;
    border: 1px solid #ccc;
    border-radius: 4px;
    box-sizing: border-box;
}

form button {
    margin-top: 20px;
    background-color: #2099b6;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

form button:hover {
    background-color: #127291;
}

/* ============================
   Tableau des sources
   ============================ */
.table-sources {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

.table-sources th,
.table-sources td {
    border: 1px solid #ccc;
    padding: 8px;
    text-align: center;
}

.table-sources th {
    background-color: #2099b6;
    color: white;
}

.btn-download {
    display: inline-block;
    background-color: #2099b6;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    text-decoration: none;
    font-size: 0.9rem;
}

.btn-download:hover {
    background-color: #127291;
}

/* ============================
   Messages
   ============================ */
#message {
    margin-top: 20px;
    font-weight: bold;
}

/* ============================
   Double separator
   ============================ */
.double-separator {
    height: 30px;
}

/* ============================
   Banniere
   ============================ */
.banniere-container {
    width: 100%;
    text-align: center;
    background-color: #e0f2f1;
    margin-bottom: 0;
}

.banniere-container img {
    max-width: 100%;
    height: auto;
}

/* ============================
   Réactivité
   ============================ */
@media screen and (max-width: 768px) {
    .page-container {
        flex-direction: column;
    }

    .sidebar.left {
        width: 100%;
        height: 50px;
    }

    .content {
        padding: 15px;
    }
}


# \static\js\ingestion.js
#-----------------------------------------------
document.addEventListener("DOMContentLoaded", function() {

    const fournisseurSelect = document.getElementById("fournisseur");
    const sourceSelect = document.getElementById("source_id");
    const formIngestion = document.getElementById("form-ingestion");
    const messageDiv = document.getElementById("message");

    // Lorsque le fournisseur change, charger les sources correspondantes
    fournisseurSelect.addEventListener("change", function() {
        const fournisseur = this.value;
        if (!fournisseur) {
            formIngestion.style.display = "none";
            sourceSelect.innerHTML = "";
            return;
        }

        fetch(`/api/get-sources/${encodeURIComponent(fournisseur)}`)
            .then(response => response.json())
            .then(data => {
                sourceSelect.innerHTML = "";
                if (data.sources.length > 0) {
                    data.sources.forEach(src => {
                        const option = document.createElement("option");
                        option.value = src.id;
                        option.textContent = src.intitule_source;
                        sourceSelect.appendChild(option);
                    });
                    formIngestion.style.display = "block";
                } else {
                    sourceSelect.innerHTML = "<option value=''>Aucune source disponible</option>";
                    formIngestion.style.display = "none";
                }
            })
            .catch(err => {
                console.error(err);
                messageDiv.textContent = "Erreur lors du chargement des sources.";
            });
    });

    // Gestion de l'upload du fichier
    formIngestion.addEventListener("submit", function(e) {
        e.preventDefault();
        messageDiv.textContent = "";

        const formData = new FormData(formIngestion);
        formData.append("fournisseur", fournisseurSelect.value);

        fetch("/api/upload", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                messageDiv.style.color = "green";
                messageDiv.textContent = data.message;
                setTimeout(() => location.reload(), 1000); // rafraîchit la page pour afficher l'historique
            } else {
                messageDiv.style.color = "red";
                messageDiv.textContent = data.message;
            }
        })
        .catch(err => {
            console.error(err);
            messageDiv.style.color = "red";
            messageDiv.textContent = "Erreur lors de l'upload du fichier.";
        });
    });

});
