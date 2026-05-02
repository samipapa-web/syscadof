# modules/notification/services.py
#-------------------------------------------------------

import os
from config import BASE_DIR
from database import get_connection
from psycopg2.extras import RealDictCursor

# ===============================
# Liste des fichiers de sortie Excel
# ===============================
def get_output_files():
    sortie_dir = os.path.join(BASE_DIR, "data", "Sortie")
    if not os.path.exists(sortie_dir):
        return []
    return [f for f in os.listdir(sortie_dir) if f.startswith("Output_") and f.endswith(".xlsx")]

# ===============================
# Types de notification (depuis DB)
# ===============================
def get_types_notification():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT DISTINCT type_notification
            FROM notifs
            WHERE type_notification IS NOT NULL
            ORDER BY type_notification
        """)
        return [row["type_notification"] for row in cur.fetchall()]

    except Exception:
        return []

    finally:
        cur.close()
        conn.close()

# ===============================
# Modèles de notification selon le type
# ===============================
def get_modeles_par_type(type_notif):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT modele_notification
            FROM notifs
            WHERE TRIM(LOWER(type_notification)) = TRIM(LOWER(%s))
            ORDER BY modele_notification
        """, (type_notif,))

        return [row["modele_notification"] for row in cur.fetchall()]

    except Exception:
        return []

    finally:
        cur.close()
        conn.close()

# ===============================
# Données pour filtres : CENTRE et CRI
# ===============================
def get_filtres_data():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    centres = []
    cris = []

    try:
        # -------- CENTRES --------
        cur.execute("""
            SELECT centre
            FROM centre
            WHERE centre IS NOT NULL
            ORDER BY centre
        """)
        centres = [row["centre"] for row in cur.fetchall()]

        # -------- CRI --------
        cur.execute("""
            SELECT cri
            FROM cri
            WHERE cri IS NOT NULL
            ORDER BY cri
        """)
        cris = [row["cri"] for row in cur.fetchall()]

    except Exception:
        centres, cris = [], []

    finally:
        cur.close()
        conn.close()

    return centres, cris