# --------------------------
# PostgreSQL (centralisé)
# --------------------------
conn = get_connection()
cur = conn.cursor(cursor_factory=RealDictCursor)

# ---- TABLE NIU ----
cur.execute("""
    SELECT niu, raison_sociale, sigle, activite, regime, centre, etat, telephone
    FROM niu
""")
df_idu = pd.DataFrame(cur.fetchall())

if not df_idu.empty:
    df_idu.columns = df_idu.columns.str.upper()

# ---- TABLE UG ----
cur.execute("""
    SELECT centre, cdif, crif, cdia, cria, acdi, acri, ville, directeur, regional
    FROM ug
""")
df_ug = pd.DataFrame(cur.fetchall())

if not df_ug.empty:
    df_ug.columns = df_ug.columns.str.upper()

# --------------------------
# Fusion IDU (NIU)
# --------------------------
if not df_idu.empty:
    df = df.merge(df_idu, on="NIU", how="left")

# --------------------------
# Fusion UG
# --------------------------
if not df_ug.empty:
    df = df.merge(df_ug, on="CENTRE", how="left")