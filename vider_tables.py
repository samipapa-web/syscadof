# ========================================
# vider_tables.py
# ========================================

import psycopg2

# =========================================================
# VIDAGE DES TABLES (sans suppression)
# =========================================================
def vider_tables(conn):
    tables = [
        "croisements",
        "fichiers_exploites",
        "restitution",
        "notification",
        "valorisation"
    ]
        
    cur = conn.cursor()
    
    for table in tables:
        try:
            cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
            print(f"🧹 Table vidée : {table}")
        except Exception as e:
            print(f"⚠️ Erreur vidage table {table} : {e}")
    
    conn.commit()
    cur.close()
    print("✅ VIDAGE TERMINÉ")

# =========================================================
# EXECUTION
# =========================================================
if __name__ == "__main__":
    conn = psycopg2.connect(
    "postgresql://syscadof_user:zAg9wpsLt0JY4n1o7jMm7hrWkvnIMdvD@dpg-d731ru6uk2gs73e8cag0-a.oregon-postgres.render.com/syscadof"
    )
    vider_tables(conn)
    conn.close()