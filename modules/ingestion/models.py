# modules/ingestion/models.py

from database import get_connection

def init_db():
    """
    Initialise les tables pour PostgreSQL.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Table sources
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sources (
            id SERIAL PRIMARY KEY,
            intitule TEXT NOT NULL,
            provenance TEXT,
            fournisseur TEXT,
            categorie TEXT,
            temporalite TEXT
        )
    """)

    # Table fichiers
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fichiers (
            id SERIAL PRIMARY KEY,
            source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE,
            annee INTEGER,
            mois INTEGER,
            type_fichier TEXT,
            date_stockage TIMESTAMP,
            stockeur TEXT,
            chemin TEXT
        )
    """)

    # Table sources_lac (historique LAC)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sources_lac (
            id SERIAL PRIMARY KEY,
            source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE,
            intitule_source TEXT,
            provenance TEXT,
            fournisseur TEXT,
            categorie TEXT,
            temporalite TEXT,
            annee INTEGER,
            mois INTEGER,
            type_fichier TEXT,
            chemin TEXT,
            nom_fichier TEXT,
            taille BIGINT,
            hash_fichier TEXT,
            utilisateur TEXT,
            date_stockage TIMESTAMP
        )
    """)

    # Table sources_clean (copie pour nettoyage)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sources_clean (
            id SERIAL PRIMARY KEY,
            source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE,
            intitule_source TEXT,
            provenance TEXT,
            fournisseur TEXT,
            categorie TEXT,
            temporalite TEXT,
            annee INTEGER,
            mois INTEGER,
            type_fichier TEXT,
            chemin TEXT,
            nom_fichier TEXT,
            taille BIGINT,
            hash_fichier TEXT,
            utilisateur TEXT,
            date_stockage TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()