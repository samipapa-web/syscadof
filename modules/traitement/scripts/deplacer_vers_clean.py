import os
import shutil
import sys
from contextlib import contextmanager
from psycopg2.extras import RealDictCursor

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(BASE_PATH)

from config import BASE_DIR, SORTIE_DIR, DATA_LAC_DIR, DATA_CLEAN_DIR
from database import get_connection, release_connection


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
# INPUT
# =========================================================
source_lac_id = int(os.environ.get("source_lac_id", 0))

if not source_lac_id:
    print("Erreur : source_lac_id non défini", file=sys.stderr)
    sys.exit(1)


try:
    # =========================================================
    # DB
    # =========================================================
    with db_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            cur.execute("SELECT * FROM sources_lac WHERE id=%s", (source_lac_id,))
            source = cur.fetchone()

            if not source:
                print("Source introuvable", file=sys.stderr)
                sys.exit(1)

            nom_fichier = source["nom_fichier"]
            annee = source["annee"]
            mois = source["mois"]

    # =========================================================
    # PATHS
    # =========================================================
    chemin_source = os.path.join(DATA_LAC_DIR, nom_fichier)

    if not os.path.exists(chemin_source):
        print(f"Fichier source introuvable : {chemin_source}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(DATA_CLEAN_DIR, exist_ok=True)

    nom_clean = f"clean_{annee}_{mois}_{nom_fichier}"
    chemin_clean = os.path.join(DATA_CLEAN_DIR, nom_clean)

    # =========================================================
    # COPIE UNIQUEMENT
    # =========================================================
    shutil.copy2(chemin_source, chemin_clean)

    # =========================================================
    # OUTPUT
    # =========================================================
    print(f"{chemin_clean}||{nom_clean}")

except Exception as e:
    print(f"Erreur traitement fichier : {e}", file=sys.stderr)
    sys.exit(1)
