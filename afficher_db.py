import psycopg2


conn = psycopg2.connect(
    "postgresql://syscadof_user:zAg9wpsLt0JY4n1o7jMm7hrWkvnIMdvD@dpg-d731ru6uk2gs73e8cag0-a.oregon-postgres.render.com/syscadof"
)

cur = conn.cursor()

# ✅ 1. Lister les tables
print("=== LISTE DES TABLES ===")
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public';
""")

tables = cur.fetchall()

for table in tables:
    print("-", table[0])

# ✅ 2Vérifier si la table users est vide
cur.execute("SELECT COUNT(*) FROM niu;")
count = cur.fetchone()[0]

if count == 0:
    print("❌ La table 'niu' est vide.")
else:
    print(f"✅ La table 'niu' contient {count} enregistrements.\n")

    # Afficher quelques lignes
    cur.execute("SELECT * FROM niu LIMIT 10;")
    rows = cur.fetchall()

    for row in rows:
        print(row)

cur.close()
conn.close()

