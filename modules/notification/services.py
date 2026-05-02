# modules/notification/services.py
#-------------------------------------------------------

import os
from contextlib import contextmanager
from flask import current_app
from psycopg2.extras import RealDictCursor

from database import get_connection, release_connection


@contextmanager
def db_conn():
    conn = get_connection()
    try:
        yield conn
    finally:
        release_connection(conn)


# ===============================
# FICHIERS SORTIE
# ===============================
def get_output_files():
    sortie_dir = current_app.config["SORTIE_DIR"]
    if not os.path.exists(sortie_dir):
        return []
    return [
        f for f in os.listdir(sortie_dir)
        if f.startswith("Output_") and f.endswith(".xlsx")
    ]


# ===============================
# TYPES NOTIF
# ===============================
def get_types_notification():
    with db_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT DISTINCT type_notification
                FROM notifs
                WHERE type_notification IS NOT NULL
                ORDER BY type_notification
            """)
            return [r["type_notification"] for r in cur.fetchall()]


# ===============================
# MODELES
# ===============================
def get_modeles_par_type(type_notif):
    with db_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT modele_notification
                FROM notifs
                WHERE LOWER(type_notification) = LOWER(%s)
            """, (type_notif,))
            return [r["modele_notification"] for r in cur.fetchall()]


# ===============================
# FILTRES
# ===============================
def get_filtres_data():
    with db_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            cur.execute("SELECT centre FROM centre ORDER BY centre")
            centres = [r["centre"] for r in cur.fetchall()]

            cur.execute("SELECT cri FROM cri ORDER BY cri")
            cris = [r["cri"] for r in cur.fetchall()]

    return centres, cris
