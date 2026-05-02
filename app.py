#app.py
#--------------------------------------------------

# ========================================
# SYSCADOF - Flask + PostgreSQL (PROPRE)
# ========================================

import os
from flask import Flask, render_template, request, redirect, session
import config
import psycopg2
from psycopg2.extras import RealDictCursor

# =========================================================
# CONFIGURATION DB
# =========================================================
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

# =========================================================
# FLASK INIT
# =========================================================
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "samipapa")
app.config.from_object(config)

# 🔥 IMPORTANT : injection dans Flask (CORRECTION PRINCIPALE)
app.get_db_connection = get_db_connection

# =========================================================
# CONTEXT PROCESSOR (DB)
# =========================================================
@app.context_processor
def inject_user_modules():

    role = session.get("role")
    modules = {}

    if role:
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT permissions FROM roles WHERE role_name = %s
            """, (role,))

            result = cur.fetchone()

            cur.close()
            conn.close()

            if result:
                modules = result["permissions"]

        except Exception as e:
            print("Erreur modules:", e)

    return dict(
        user=session.get("user"),
        role=role,
        modules=modules
    )

# =========================================================
# AUTH FUNCTIONS
# =========================================================
def authenticate(username, password):

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM users WHERE username = %s
        """, (username,))

        user = cur.fetchone()

        cur.close()
        conn.close()

        if not user:
            return None

        if user["password"] != password:
            return None

        return user

    except Exception as e:
        print("Erreur auth:", e)
        return None


def login_required(f):
    from functools import wraps

    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return redirect("/login")
        return f(*args, **kwargs)

    return wrapper


# =========================================================
# IMPORT MODULES
# =========================================================
from modules.ingestion.routes import ingestion_bp
from modules.traitement.routes import traitement_bp
from modules.traitement.insert_scripts import sync_scripts_to_db
from modules.analyse.routes import analyse_bp
from modules.exploitation.routes import exploitation_bp
from modules.valorisation.routes import valorisation_bp
from modules.notification.routes import notification_bp
from modules.notification.routes_doc import doc_bp
from modules.administration.routes import administration_bp
from modules.revue.routes_revue import revue_bp 

with app.app_context():
    sync_scripts_to_db()

# =========================================================
# BLUEPRINTS
# =========================================================
app.register_blueprint(ingestion_bp, url_prefix="/ingestion")
app.register_blueprint(traitement_bp, url_prefix="/traitement")
app.register_blueprint(analyse_bp, url_prefix="/analyse")
app.register_blueprint(exploitation_bp, url_prefix="/exploitation")
app.register_blueprint(valorisation_bp, url_prefix="/valorisation")
app.register_blueprint(notification_bp)
app.register_blueprint(doc_bp, url_prefix="/notification")
app.register_blueprint(administration_bp, url_prefix="/administration")
app.register_blueprint(revue_bp)

# =========================================================
# ROUTES
# =========================================================
@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = authenticate(username, password)

        if user:
            session["user"] = user["username"]
            session["role"] = user["role_name"]
            return redirect("/")

        return render_template("login.html", error="Identifiants incorrects")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# =========================================================
# ERREURS
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
# TEST DB
# =========================================================
@app.route("/test_db")
@login_required
def test_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS total FROM sources_donnees;")
    result = cur.fetchone()

    cur.close()
    conn.close()

    return f"Total sources_donnees: {result['total']}"


# =========================================================
# RUN
# =========================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)