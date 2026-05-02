#
# MODULE 0: CONNECTION ET ACCUEIL
#########################################################

#
# Init_database.py
# ----------------------------------

import sqlite3

DB_PATH = "syscadof.db"

sql_script = """
CREATE TABLE IF NOT EXISTS sources_donnees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intitule_source TEXT NOT NULL,
    provenance TEXT NOT NULL CHECK (provenance IN ('Interne', 'Externe')),
    fournisseur TEXT NOT NULL,
    categorie TEXT NOT NULL,
    temporalite TEXT NOT NULL CHECK (temporalite IN ('Stock', 'Flux annuel', 'Flux mensuel')),
    type_fichier TEXT,
    actif INTEGER NOT NULL DEFAULT 1
);

INSERT OR IGNORE INTO sources_donnees
(intitule_source, provenance, fournisseur, categorie, temporalite)
VALUES
('Fichier des opérations bancaires internationales', 'Externe', 'ANIF', 'Banques', 'Flux annuel'),
('Fichier des opérations bancaires', 'Externe', 'ANIF', 'Banques', 'Flux annuel'),
('Fichier des comptes bancaires dormants', 'Externe', 'BEAC', 'Banques', 'Stock'),
('Fichier des opérations bancaires internationales', 'Externe', 'BEAC', 'Banques', 'Flux annuel'),
('Fichier des opérations bancaires', 'Externe', 'BEAC', 'Banques', 'Flux annuel'),
('Fichier des paiements bancaires offshore', 'Externe', 'BEAC', 'Banques', 'Flux annuel'),
('Registre central des conservateurs fonciers', 'Externe', 'CADASTRE', 'Immatriculations', 'Stock'),
('Fichier de la CNPS', 'Externe', 'CNPS', 'Identification', 'Stock'),
('Fichier des attestations des exportations effectives', 'Externe', 'DGD', 'Commerce', 'Flux annuel'),
('Fichier douanier des exportations', 'Externe', 'DGD', 'Commerce', 'Flux annuel'),
('Fichier douanier des importations', 'Externe', 'DGD', 'Commerce', 'Flux annuel'),
('Fichier global des opérations douanières', 'Externe', 'DGD', 'Commerce', 'Flux annuel'),
('Base DSF SMT – Compte de résultat', 'Interne', 'DGI', 'DSF', 'Flux annuel'),
('Base DSF Système normale – Compte de résultat', 'Interne', 'DGI', 'DSF', 'Flux annuel'),
('Base DSF Système normale – Note 21', 'Interne', 'DGI', 'DSF', 'Flux annuel'),
('Base DSF Système normale – Note 22', 'Interne', 'DGI', 'DSF', 'Flux annuel'),
('Base DSF Système normale – Note 3A (Amortissements)', 'Interne', 'DGI', 'DSF', 'Flux annuel'),
('Base DSF Système normale – Note 3C (Immobilisations)', 'Interne', 'DGI', 'DSF', 'Flux annuel'),
('Base DSF Système normale – Note CF2 (Déductions TVA)', 'Interne', 'DGI', 'DSF', 'Flux annuel'),
('Base DSF Système normale – Note R2', 'Interne', 'DGI', 'DSF', 'Flux annuel'),
('Base DSF Système normale – Note R3', 'Interne', 'DGI', 'DSF', 'Flux annuel'),
('Base DSF – Soldes déclarés', 'Interne', 'DGI', 'DSF', 'Flux annuel'),
('Fichier consolidé des DIPE', 'Interne', 'DGI', 'Annexes DSF', 'Flux annuel'),
('Fichier consolidé des listings clients locaux', 'Interne', 'DGI', 'Annexes DSF', 'Flux annuel'),
('Fichier consolidé des listings clients étrangers', 'Interne', 'DGI', 'Annexes DSF', 'Flux annuel'),
('Fichier consolidé des listings fournisseurs locaux', 'Interne', 'DGI', 'Annexes DSF', 'Flux annuel'),
('Fichier consolidé des listings fournisseurs étrangers', 'Interne', 'DGI', 'Annexes DSF', 'Flux annuel'),
('Fichier consolidé des sommes versées aux tiers locaux', 'Interne', 'DGI', 'Annexes DSF', 'Flux annuel'),
('Fichier consolidé des sommes versées aux tiers étrangers', 'Interne', 'DGI', 'Annexes DSF', 'Flux annuel'),
('Base E-Billing', 'Interne', 'DGI', 'Recettes fiscales', 'Flux annuel'),
('Fichier des paiements des impôts et taxes – HARMONY2', 'Interne', 'DGI', 'Recettes fiscales', 'Flux annuel'),
('Fichier des paiements des impôts et taxes – MESURE', 'Interne', 'DGI', 'Recettes fiscales', 'Flux annuel'),
('Fichier des paiements des impôts et taxes – OTP', 'Interne', 'DGI', 'Recettes fiscales', 'Flux annuel'),
('Fichier des paiements des impôts et taxes – SYSTAC', 'Interne', 'DGI', 'Recettes fiscales', 'Flux annuel'),
('Fichier de déclaration des déductions', 'Interne', 'DGI', 'Déclarations fiscales', 'Flux annuel'),
('Fichier des déclarations annuelles des revenus', 'Interne', 'DGI', 'Déclarations fiscales', 'Flux annuel'),
('Fichier des déclarations des droits d''enregistrement', 'Interne', 'DGI', 'Déclarations fiscales', 'Flux annuel'),
('Fichier des déclarations des restructurations des sociétés', 'Interne', 'DGI', 'Déclarations fiscales', 'Flux annuel'),
('Fichier des déclarations mensuelles IGS', 'Interne', 'DGI', 'Déclarations fiscales', 'Flux mensuel'),
('Fichier des déclarations mensuelles IR & TVA', 'Interne', 'DGI', 'Déclarations fiscales', 'Flux mensuel'),
('Fichier des déclarations mensuelles synthétiques', 'Interne', 'DGI', 'Déclarations fiscales', 'Flux mensuel'),
('Fichier des AMR', 'Interne', 'DGI', 'Dettes fiscales', 'Stock'),
('Fichier des états de suivi des moratoires', 'Interne', 'DGI', 'Dettes fiscales', 'Stock'),
('Registre des bénéficiaires effectifs', 'Interne', 'DGI', 'Déclarations fiscales', 'Flux annuel'),
('Registre des contribuables actifs', 'Interne', 'DGI', 'Déclarations fiscales', 'Flux annuel'),
('Registre des contribuables inactifs', 'Interne', 'DGI', 'Déclarations fiscales', 'Flux annuel'),
('Registre des agréments d''importation', 'Externe', 'MINCOMMERCE', 'Autorisations', 'Stock'),
('Fichier des autorisations de travail et visas de travail', 'Externe', 'MINEFOP', 'Autorisations', 'Stock'),
('Fichier des exonérations fiscales', 'Externe', 'MINFI', 'Autorisations', 'Stock'),
('Fichier des opérateurs du secteur forestier', 'Externe', 'MINFOF', 'Immatriculations', 'Flux annuel'),
('Registre des titres d''exploitation forestière', 'Externe', 'MINFOF', 'Autorisations', 'Stock'),
('Fichier des GIC et sociétés coopératives', 'Externe', 'MINJUSTICE', 'Immatriculations', 'Stock'),
('Fichier des registres de commerce', 'Externe', 'MINJUSTICE', 'Immatriculations', 'Stock'),
('Fichier des opérateurs du secteur minier', 'Externe', 'MINMIDT', 'Immatriculations', 'Stock'),
('Registre des titres d''exploration ou d''exploitation minière', 'Externe', 'MINMIDT', 'Autorisations', 'Stock'),
('Fichier des opérateurs du secteur transport routier', 'Externe', 'MINTRANSPORT', 'Immatriculations', 'Stock');

CREATE TABLE IF NOT EXISTS sources_lac (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    intitule_source TEXT NOT NULL,
    provenance TEXT NOT NULL,
    fournisseur TEXT NOT NULL,
    categorie TEXT NOT NULL,
    temporalite TEXT NOT NULL,
    annee INTEGER NOT NULL,
    mois INTEGER DEFAULT 0,
    type_fichier TEXT NOT NULL,
    chemin TEXT NOT NULL,
    nom_fichier TEXT NOT NULL,
    taille INTEGER,
    hash_fichier TEXT,
    utilisateur TEXT NOT NULL,
    date_stockage TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sources_clean (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    intitule_source TEXT NOT NULL,
    provenance TEXT NOT NULL,
    fournisseur TEXT NOT NULL,
    categorie TEXT NOT NULL,
    temporalite TEXT NOT NULL,
    annee INTEGER NOT NULL,
    mois INTEGER DEFAULT 0,
    type_fichier TEXT NOT NULL,
    chemin TEXT NOT NULL,
    nom_fichier TEXT NOT NULL,
    taille INTEGER,
    hash_fichier TEXT,
    utilisateur TEXT NOT NULL,
    date_stockage TEXT NOT NULL,
    date_apurement TEXT,       -- pour log traitement
    script_utilise TEXT,       -- script qui a traité la source
    statut TEXT                -- Succès ou Erreur
);

CREATE TABLE IF NOT EXISTS base_scripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    object TEXT NOT NULL,
    auteur TEXT NOT NULL,
    chemin_script TEXT NOT NULL,
    date_stockage TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS restitution (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_fichier TEXT,
    chapitre TEXT,
    risque TEXT,
    axe TEXT,
    script_utilise TEXT,
    utilisateur TEXT,
    impots_inclus TEXT,
    date_generation TEXT
);

CREATE TABLE IF NOT EXISTS notification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notification TEXT,
    nom_fichier TEXT,
    type_notification TEXT,
    script_utilise TEXT,
    utilisateur TEXT,
    date_creation TEXT
);
"""

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()
    print("Base syscadof.db initialisée correctement.")

if __name__ == "__main__":
    main()


#
# App.py
#-----------------------------------

# =========================================================
# SYSCADOF - Application principale
# =========================================================

import os
from flask import Flask, render_template, request, redirect, session
from security.auth import load_roles_users, USERS, roles_access, login_required

# =========================================================
# IMPORT DES BLUEPRINTS
# =========================================================
from modules.ingestion.routes import ingestion_bp
from modules.traitement.routes import traitement_bp
from modules.analyse.routes import analyse_bp
from modules.exploitation.routes import exploitation_bp
from modules.valorisation.routes import valorisation_bp
from modules.notification.routes import notification_bp
from modules.notification.routes_doc import doc_bp
from modules.administration.routes import administration_bp


# =========================================================
# INITIALISATION FLASK
# =========================================================
app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_LAC_DIR = os.path.join(BASE_DIR, "data", "lac")
DATA_CLEAN_DIR = os.path.join(BASE_DIR, "data", "clean")
SORTIE_DIR = os.path.join(DATA_DIR, "Sortie")
DB_PATH = os.path.join(BASE_DIR, "syscadof.db")

app.config["DATA_DIR"] = DATA_DIR
app.config["SORTIE_DIR"] = SORTIE_DIR
app.config["DB_PATH"] = DB_PATH

# Création automatique des dossiers
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SORTIE_DIR, exist_ok=True)

# =========================================================
# CHARGEMENT DES RÔLES ET UTILISATEURS
# =========================================================
EXCEL_PATH = os.path.join(DATA_DIR, "templates", "ROLES.xlsx")
load_roles_users(EXCEL_PATH)

# =========================================================
# CONTEXT PROCESSOR GLOBAL
# =========================================================
@app.context_processor
def inject_user_modules():

    user = session.get("user")
    role = session.get("role")

    modules = roles_access.get(role, {}) if role else {}

    return dict(
        user=user,
        role=role,
        modules=modules
    )

# =========================================================
# ENREGISTREMENT DES BLUEPRINTS
# =========================================================
app.register_blueprint(ingestion_bp, url_prefix="/ingestion")
app.register_blueprint(traitement_bp, url_prefix="/traitement")
app.register_blueprint(analyse_bp, url_prefix="/analyse")
app.register_blueprint(exploitation_bp, url_prefix="/exploitation")
app.register_blueprint(valorisation_bp, url_prefix="/valorisation")
app.register_blueprint(notification_bp)
app.register_blueprint(doc_bp, url_prefix="/notification")
app.register_blueprint(administration_bp, url_prefix="/administration")

# =========================================================
# ROUTES PRINCIPALES
# =========================================================
@app.route("/")
@login_required
def index():
    return render_template("index.html")

# =========================================================
# LOGIN
# =========================================================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = USERS.get(username)

        if user and user["password"] == password:

            # SESSION PRINCIPALE
            session["user"] = username
            session["role"] = user["role"]

            # COMPATIBILITÉ AVEC CERTAINS MODULES
            session["username"] = username

            return redirect("/")

        return render_template("login.html", error="Identifiants incorrects")

    return render_template("login.html")

# =========================================================
# LOGOUT
# =========================================================
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

# =========================================================
# GESTION DES ERREURS
# =========================================================
@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

# =========================================================
# LANCEMENT
# =========================================================
if __name__ == "__main__":
    app.run(debug=True)

#
# \Templates\login.html
#-------------------------------------

<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>SYSCADOF - Login</title>

<style>

*{
    box-sizing:border-box;
}

body{
    font-family: Arial, Helvetica, sans-serif;
    background:#f4f6f9;
    display:flex;
    justify-content:center;
    align-items:center;
    height:90vh;
    margin:0;
}

.login-box{
    background:white;
    padding:30px;
    border-radius:5px;
    box-shadow:0 3px 10px rgba(0,0,0,0.1);
    width:350px;
    text-align:center;
}

/* Titres */

.login-box h2{
    font-size:32px;
    color:#127291;
    margin-bottom:0;
    font-weight:bold;
    text-align:left;
}

.login-box h3{
    font-size:24px;
    color:#127291;
    margin-bottom:8px;
    font-weight:normal;
}

.login-box h4{
    font-size:16px;
    color:#475569;
    margin-bottom:10px;
    font-weight:normal;
    text-align:left;
}

/* Champs formulaire */

.login-box input[type="text"],
.login-box input[type="password"]{
    width:100%;
    padding:10px;
    margin:10px 0;
    border-radius:5px;
    border:1px solid #ccc;
    font-size:14px;
}

/* Bouton */

.login-box button{
    width:100%;
    padding:10px;
    margin-top:10px;
    border:none;
    border-radius:5px;
    background:#127291;
    color:white;
    font-weight:bold;
    cursor:pointer;
    font-size:16px;
}

.login-box button:hover{
    background:#0d5a72;
}

/* Message erreur */

.error-msg{
    color:#dc2626;
    text-align:center;
    margin-top:10px;
    font-weight:bold;
}

</style>

</head>

<body>

<div class="login-box">

<h2>SYSCADOF</h2>
<h4>Entrez vos paramètres de connexion</h4>

<form method="POST" action="/login">

<input 
type="text" 
name="username" 
placeholder="Utilisateur" 
required>

<input 
type="password" 
name="password" 
placeholder="Mot de passe" 
required>

<button type="submit">
Se connecter
</button>

</form>

{% if error %}
<div class="error-msg">
{{ error }}
</div>
{% endif %}

</div>

</body>
</html>

#
# \Templates\index.html
#-------------------------------------

<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>SYSCADOF - Accueil</title>

<style>

/* ================================
STRUCTURE GENERALE
================================ */

body{
    margin:0;
    font-family:Arial, Helvetica, sans-serif;
    background:#f4f6f9;
}

/* ============================
BANNIERE FIXE
============================ */

.banniere-container{
    position:fixed;
    top:0;
    left:0;
    width:100%;
    z-index:1000;
}

.banniere-container img{
    width:100%;
    height:auto;
    display:block;
}

/* ============================
VARIABLE DYNAMIQUE
============================ */

:root{
    --banner-height:0px;
}

/* ============================
MENU HORIZONTAL
============================ */

.sidebar{
    position:fixed;
    top:var(--banner-height);
    left:0;
    width:100%;
    height:55px;
    background:#1e293b;
    display:flex;
    justify-content:center;
    align-items:center;
    z-index:900;
}

.sidebar a{
    margin:0 8px;
    padding:10px 18px;
    color:white;
    text-decoration:none;
    font-weight:bold;
    border-radius:4px;
    background:#127291;
    font-size:13px;
}

.sidebar a:hover{
    background:#0d5a72;
}

.logout{
    background:#dc2626 !important;
}

/* ================================
UTILISATEUR CONNECTÉ
================================ */

.user-bar{
    position:fixed;
    right:20px;
    top:calc(var(--banner-height) + 65px);
    font-size:13px;
    color:#333;
}

/* ================================
CONTENU PRINCIPAL
================================ */

.main{
    margin-top:calc(var(--banner-height) + 90px);
    padding:20px;
    max-width:1200px;
    margin-left:auto;
    margin-right:auto;
}

/* ================================
CARDS MODULES – UNE SEULE LIGNE
================================ */

.cards{
    display:flex;
    gap:25px;
    justify-content:center;
    flex-wrap:wrap;
    padding-bottom:10px;
}

.cards::-webkit-scrollbar{
    height:6px;
}

.cards::-webkit-scrollbar-thumb{
    background:#127291;
    border-radius:3px;
}

.card{
    flex:0 0 120px;
    background:white;
    padding:25px;
    border-radius:10px;
    box-shadow:0 3px 10px rgba(0,0,0,0.08);
    cursor:pointer;
    transition:all 0.25s ease;
    position:relative;
    overflow:hidden;
}

.card::before{
    content:"";
    position:absolute;
    top:0;
    left:0;
    width:100%;
    height:5px;
}

.card:hover{
    transform:translateY(-6px);
    box-shadow:0 8px 20px rgba(0,0,0,0.15);
    background:#127291;
}

.card-title{
    font-size:18px;
    font-weight:bold;
    margin-bottom:8px;
    transition:0.2s;
}

.card-desc{
    font-size:14px;
    color:#555;
    transition:0.2s;
}

.card:hover .card-title,
.card:hover .card-desc{
    color:white;
}

/* ================================
COULEURS PAR MODULE
================================ */

.card.ingestion::before{ background:#2563eb; }
.card.apurement::before{ background:#16a34a; }
.card.analyse::before{ background:#9333ea; }
.card.exploitation::before{ background:#ea580c; }
.card.valorisation::before{ background:#d97706; }
.card.notification::before{ background:#dc2626; }

</style>
</head>

<body>

<!-- ============================
BANNIERE
============================ -->

<div class="banniere-container">
<img id="banner"
src="{{ url_for('static', filename='images/accueil.jpg') }}"
alt="Bannière">
</div>

<!-- ============================
MENU DYNAMIQUE
============================ -->

<nav class="sidebar">

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

{% if modules.get("Administration") %}
<a href="/administration">Administration</a>
{% endif %}

<a href="/logout" class="logout">Déconnexion</a>

</nav>

<!-- ============================
UTILISATEUR CONNECTÉ
============================ -->

<div class="user-bar">
Utilisateur : <b>{{ user }}</b> |
Rôle : <b>{{ role }}</b>
</div>

<!-- ============================
CONTENU
============================ -->

<div class="main">

<div class="cards">

{% if modules.get("Ingestion") %}
<div class="card ingestion" onclick="location.href='/ingestion'">
<div class="card-title">Ingestion</div>
<div class="card-desc">Importation, organisation et stockage des données de diverses sources</div>
</div>
{% endif %}

{% if modules.get("Apurement") %}
<div class="card apurement" onclick="location.href='/traitement/editor'">
<div class="card-title">Apurement</div>
<div class="card-desc">Nettoyage et préparation des données stockées</div>
</div>
{% endif %}

{% if modules.get("Croisement") %}
<div class="card analyse" onclick="location.href='/analyse'">
<div class="card-title">Croisement</div>
<div class="card-desc">Croisement des données et détection des entités à risque</div>
</div>
{% endif %}

{% if modules.get("Orientation") %}
<div class="card exploitation" onclick="location.href='/exploitation'">
<div class="card-title">Orientation</div>
<div class="card-desc">Validation du listing des entités à risque, orientation de l'exploitation</div>
</div>
{% endif %}

{% if modules.get("Valorisation") %}
<div class="card valorisation" onclick="location.href='/valorisation'">
<div class="card-title">Valorisation</div>
<div class="card-desc">Complément d'informations et liquidation des impôts dus</div>
</div>
{% endif %}

{% if modules.get("Restitution") %}
<div class="card notification" onclick="location.href='/notification'">
<div class="card-title">Restitution</div>
<div class="card-desc">Génération des outputs pour notification</div>
</div>
{% endif %}

</div>

</div>

<!-- ============================
SCRIPT BANNIERE
============================ -->

<script>

function ajusterBanniere(){

let banner=document.getElementById("banner");

if(banner){

let h=banner.offsetHeight;

document.documentElement.style.setProperty("--banner-height",h+"px");

}

}

window.onload=ajusterBanniere;

window.onresize=ajusterBanniere;

</script>

</body>
</html>

#
# \security\auth.py
#------------------------------------

import os
import pandas as pd
from flask import session, redirect, render_template
from functools import wraps


roles_access = {}
USERS = {}


def load_roles_users(excel_path):

    global roles_access
    global USERS

    if not os.path.exists(excel_path):
        print("Fichier ROLES.xlsx introuvable")
        return

    # -----------------------------
    # CHARGEMENT DES ROLES
    # -----------------------------
    roles_df = pd.read_excel(excel_path, sheet_name="ROLES")

    for _, row in roles_df.iterrows():

        role = str(row["Role"]).strip()

        modules = {
            col: str(row[col]).strip().lower() == "oui"
            for col in roles_df.columns
            if col != "Role"
        }

        roles_access[role] = modules

    # -----------------------------
    # CHARGEMENT DES UTILISATEURS
    # -----------------------------
    users_df = pd.read_excel(excel_path, sheet_name="USERS")

    for _, row in users_df.iterrows():

        username = str(row["Utilisateur"]).strip()

        USERS[username] = {
            "password": str(row["Mot de passe"]).strip(),
            "role": str(row["Role"]).strip()
        }


# ======================================================
# DECORATEUR LOGIN
# ======================================================

def login_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if "user" not in session:
            return redirect("/login")

        return f(*args, **kwargs)

    return wrapper


# ======================================================
# DECORATEUR ROLE
# ======================================================

def access_required(module):

    def decorator(f):

        @wraps(f)
        def wrapper(*args, **kwargs):

            role = session.get("role")

            if not role:
                return redirect("/login")

            allowed = roles_access.get(role, {}).get(module, False)

            if not allowed:
                return render_template("403.html"), 403

            return f(*args, **kwargs)

        return wrapper

    return decorator

