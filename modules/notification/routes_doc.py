# routes_doc.py
#---------------------------------------

from flask import Blueprint, request, send_from_directory, jsonify
import os
from werkzeug.utils import secure_filename
from psycopg2.extras import RealDictCursor

from database import get_connection, release_connection
from contextlib import contextmanager
from config import TEMPLATES_DIR


doc_bp = Blueprint("doc_bp", __name__)


@contextmanager
def db_conn():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        release_connection(conn)

# ===============================
# LISTER LES TEMPLATES
# ===============================
@doc_bp.route("/api/templates")
def get_templates():

    try:
        os.makedirs(TEMPLATES_DIR, exist_ok=True)

        files = [
            f for f in os.listdir(TEMPLATES_DIR)
            if f.lower().endswith(".docx")
        ]

        return jsonify(files)

    except Exception as e:
        return jsonify([])

# ===============================
# OUVRIR UN TEMPLATE
# ===============================
@doc_bp.route("/template/<path:nom>")
def get_template(nom):

    safe = secure_filename(nom)
    path = os.path.join(TEMPLATES_DIR, safe)

    if not os.path.exists(path):
        return "Modèle introuvable", 404

    return send_from_directory(TEMPLATES_DIR, safe)

# ===============================
# TYPES
# ===============================
@doc_bp.route("/api/types_notification")
def get_types_notification():

    with db_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT DISTINCT type_notification
                FROM notifs
                ORDER BY type_notification
            """)
            return jsonify([r["type_notification"] for r in cur.fetchall()])


# ===============================
# UPLOAD TEMPLATE
# ===============================
@doc_bp.route("/api/upload_template", methods=["POST"])
def upload_template():

    file = request.files.get("file")
    type_notif = request.form.get("type_notification")
    intitule = request.form.get("intitule")

    if not file or not type_notif or not intitule:
        return jsonify(success=False, message="Champs manquants")

    if not file.filename.lower().endswith(".docx"):
        return jsonify(success=False, message="Format invalide")

    os.makedirs(TEMPLATES_DIR, exist_ok=True)

    filename = secure_filename(intitule) + ".docx"
    path = os.path.join(TEMPLATES_DIR, filename)

    if os.path.exists(path):
        return jsonify(success=False, message="Existe déjà")

    file.save(path)

    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO notifs (type_notification, modele_notification)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (type_notif, intitule))

    return jsonify(success=True, message="Modèle enregistré")
