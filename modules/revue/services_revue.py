# modules/revue/services_revue.py
#-------------------------------------------------------

from contextlib import contextmanager
from psycopg2.extras import RealDictCursor
from database import get_connection, release_connection

@contextmanager
def db_conn():
    conn = get_connection()
    try:
        yield conn
    finally:
        release_connection(conn)

def get_filtres_data():
    with db_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            cur.execute("SELECT centre FROM centre ORDER BY centre")
            centres = [r["centre"] for r in cur.fetchall()]

            cur.execute("SELECT cri FROM cri ORDER BY cri")
            cris = [r["cri"] for r in cur.fetchall()]

    return centres, cris