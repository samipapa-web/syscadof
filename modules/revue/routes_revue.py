# modules/revue/routes_revue.py
#---------------------------------------

from flask import Blueprint, render_template, jsonify, request, current_app, send_from_directory
import os
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from database import get_connection, release_connection

from .services_revue import get_filtres_data
from .scripts.script_revue import run_revue

revue_bp = Blueprint("revue", __name__, url_prefix="/revue", template_folder="templates")

@contextmanager
def db_conn():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    finally:
        release_connection(conn)

@revue_bp.route("/")
def page():
    return render_template("revue.html")

@revue_bp.route("/api/init")
def init():
    centres, cris = get_filtres_data()
    return jsonify({"centres": centres, "cris": cris})

@revue_bp.route("/api/run", methods=["POST"])
def run():
    data = request.json

    try:
        result = run_revue(
            niu=data.get("niu"),
            cri=data.get("cri"),
            centre=data.get("centre"),
            sortie_dir=current_app.config["SORTIE_DIR"],
            template_dir=current_app.config["TEMPLATES_DIR"]
        )
        return jsonify(success=True, **result)

    except Exception as e:
        return jsonify(success=False, message=str(e))

@revue_bp.route("/download/<path:nom>")
def download(nom):
    return send_from_directory(
        current_app.config["SORTIE_DIR"],
        nom,
        as_attachment=True
    )