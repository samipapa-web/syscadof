# routes.py
#---------------------------------------
import os
import importlib
from contextlib import contextmanager

from flask import (
    Blueprint, render_template, jsonify,
    request, current_app, send_from_directory, session
)

from werkzeug.utils import secure_filename
from psycopg2.extras import RealDictCursor

from database import get_connection, release_connection
from .services import (
    get_output_files,
    get_types_notification,
    get_filtres_data,
    get_modeles_par_type
)

modules = {
    "Ingestion": True,
    "Apurement": True,
    "Croisement": True,
    "Orientation": True,
    "Valorisation": True,
    "Restitution": True
}

notification_bp = Blueprint(
    "notification",
    __name__,
    url_prefix="/notification",
    template_folder="templates"
)

# =========================================================
# CONTEXT MANAGER DB
# =========================================================
@contextmanager
def db_conn():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        release_connection(conn)


# =========================================================
# PAGE PRINCIPALE
# =========================================================
@notification_bp.route("/")
def notification_page():
    return render_template("notification.html", modules=modules)


# =========================================================
# INIT
# =========================================================
@notification_bp.route("/api/init")
def init_data():
    return jsonify({
        "files": get_output_files(),
        "types_notif": get_types_notification(),
        "centres": get_filtres_data()[0],
        "cris": get_filtres_data()[1]
    })


# =========================================================
# MODELES
# =========================================================
@notification_bp.route("/api/modeles")
def modeles_par_type():
    type_notif = request.args.get("type")
    if not type_notif:
        return jsonify([])
    return jsonify(get_modeles_par_type(type_notif))


# =========================================================
# EXECUTION SCRIPT
# =========================================================
@notification_bp.route("/api/execute", methods=["POST"])
def execute_script():

    data = request.json
    utilisateur = session.get("user", "system")

    try:
        module = importlib.import_module(
            "modules.notification.scripts.script_notification"
        )

        # ✅ UNE SEULE CONNEXION DB
        with db_conn() as conn:
            result = module.run_notif(
                fichier=data.get("fichier"),
                niu=data.get("niu"),
                centre=data.get("centre"),
                cri=data.get("cri"),
                type_personne=data.get("type_personne"),
                type_notification=data.get("type_notification"),
                modele=data.get("modele"),
                sortie_dir=current_app.config["SORTIE_DIR"],
                conn=conn,   # ✅ CORRIGÉ
                utilisateur=utilisateur
            )

        return jsonify(success=True, **result)

    except Exception as e:
        current_app.logger.error(f"ERREUR notification: {e}")
        return jsonify(success=False, message=str(e))


# =========================================================
# HISTORIQUE
# =========================================================
@notification_bp.route("/api/historique")
def historique():
    try:
        with db_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM notification ORDER BY id DESC")
                return jsonify(cur.fetchall())

    except Exception as e:
        return jsonify([]), 500


# =========================================================
# PDF VIEWER
# =========================================================
@notification_bp.route("/pdf/<path:nom>")
def pdf_viewer(nom):
    return render_template("PDF.html", fichier=secure_filename(nom))


# =========================================================
# SERVE PDF
# =========================================================
@notification_bp.route("/pdf_file/<path:nom>")
def pdf_file(nom):

    sortie_dir = current_app.config["SORTIE_DIR"]
    safe = secure_filename(nom)

    path = os.path.join(sortie_dir, safe)

    if not os.path.exists(path):
        return "Fichier introuvable", 404

    return send_from_directory(sortie_dir, safe)


# =========================================================
# DOWNLOAD FILE
# =========================================================
@notification_bp.route("/download/<path:nom>")
def download_file(nom):

    sortie_dir = current_app.config["SORTIE_DIR"]
    safe = secure_filename(nom)

    path = os.path.join(sortie_dir, safe)

    if not os.path.exists(path):
        return "Fichier introuvable", 404

    return send_from_directory(
        sortie_dir,
        safe,
        as_attachment=True  # ✅ force le téléchargement
    )

# =========================================================
# PAGE DE CREATION DE NOUVEAU MODELE
# =========================================================
@notification_bp.route("/doc")
def doc_page():
    return render_template("doc.html", modules=modules)
