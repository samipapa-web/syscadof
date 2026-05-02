# modules/ingestion/routes.py
# -----------------------------------

import os
from flask import Blueprint, render_template, request, send_from_directory, session, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

# import centralisé pour la connexion PostgreSQL
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from database import get_connection, release_connection
import config

BASE_DIR = config.BASE_DIR
UPLOAD_FOLDER = config.DATA_LAC_DIR

ALLOWED_EXTENSIONS = {"csv", "xlsx", "txt"}

ingestion_bp = Blueprint(
    "ingestion",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/ingestion"
)

# =========================================================
# CONTEXT MANAGER DB (ANTI-FUITE)
# =========================================================
@contextmanager
def db_conn():
    conn = get_connection()
    try:
        yield conn
    finally:
        release_connection(conn)


# =========================================================
# UTILITAIRE
# =========================================================
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# =========================================================
# PAGE PRINCIPALE
# =========================================================
@ingestion_bp.route("/")
def page_ingestion():
    utilisateur = session.get("user", "inconnu")

    try:
        with db_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:

                # Historique
                cur.execute("SELECT * FROM sources_lac ORDER BY id DESC")
                sources = cur.fetchall()

                # Fournisseurs
                cur.execute("""
                    SELECT DISTINCT fournisseur
                    FROM sources_donnees
                    WHERE fournisseur IS NOT NULL
                    ORDER BY fournisseur
                """)
                fournisseurs = [row['fournisseur'] for row in cur.fetchall()]

        return render_template(
            "ingestion.html",
            sources=sources,
            fournisseurs=fournisseurs,
            current_user=utilisateur
        )

    except Exception as e:
        return render_template("500.html", erreur=str(e)), 500


# =========================================================
# API : SOURCES PAR FOURNISSEUR
# =========================================================
@ingestion_bp.route("/api/get-sources/<fournisseur>")
def get_sources(fournisseur):

    try:
        with db_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:

                cur.execute("""
                    SELECT id, intitule_source
                    FROM sources_donnees
                    WHERE TRIM(LOWER(fournisseur)) = TRIM(LOWER(%s))
                    ORDER BY intitule_source
                """, (fournisseur.strip(),))

                sources = cur.fetchall()

        return jsonify({"sources": sources})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================================================
# UPLOAD FICHIER
# =========================================================
@ingestion_bp.route("/api/upload", methods=["POST"])
def upload_file():
    utilisateur = session.get("user", "inconnu")

    try:
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

        with db_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:

                # Vérifier source
                cur.execute("SELECT * FROM sources_donnees WHERE id=%s", (source_id,))
                src = cur.fetchone()

                if not src:
                    return jsonify({"success": False, "message": "Source invalide"})

                # Insertion
                cur.execute("""
                    INSERT INTO sources_lac
                    (source_id, intitule_source, provenance, fournisseur, categorie,
                     temporalite, annee, mois, type_fichier, chemin, nom_fichier,
                     taille, hash_fichier, utilisateur, date_stockage)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    src['id'], src['intitule_source'], src['provenance'], src['fournisseur'],
                    src['categorie'], src['temporalite'],
                    annee, mois, extension, UPLOAD_FOLDER, filename,
                    taille, None, utilisateur, date_stockage
                ))

                conn.commit()

        return jsonify({"success": True, "message": "Fichier uploadé avec succès"})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# =========================================================
# TELECHARGEMENT
# =========================================================
@ingestion_bp.route("/download/<int:id>")
def download_lac(id):

    try:
        with db_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:

                cur.execute("""
                    SELECT chemin, nom_fichier
                    FROM sources_lac
                    WHERE id=%s
                """, (id,))

                row = cur.fetchone()

        if row:
            return send_from_directory(row['chemin'], row['nom_fichier'], as_attachment=True)

        return "Fichier introuvable", 404

    except Exception as e:
        return str(e), 500
