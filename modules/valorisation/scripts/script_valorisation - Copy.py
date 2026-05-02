# modules/valorisation/scripts/script_valorisation.py
# ------------------------------------------------------

import os
import pandas as pd
import numpy as np
from datetime import datetime
from psycopg2.extras import RealDictCursor

from database import get_connection
from config import SORTIE_DIR


# ===============================
# TRAITEMENT PRINCIPAL
# ===============================
def traitement_valorisation(
        fichier,
        matiere,
        risque,
        axe,
        historique_id,
        impots_inclus,
        autre_taxe=""
):

    try:
        # --------------------------
        # Chemin fichier source
        # --------------------------
        chemin_source = os.path.join(SORTIE_DIR, fichier)

        if not os.path.exists(chemin_source):
            raise FileNotFoundError(f"Fichier introuvable : {fichier}")

        # --------------------------
        # Lecture fichier
        # --------------------------
        df = pd.read_excel(chemin_source)
        df.columns = df.columns.str.strip().str.upper()

        # --------------------------
        # Normalisation colonnes
        # --------------------------
        df["VAL_RECOUP"] = df.get("TOTAL GÉNÉRAL", 0)
        df["VAL_DECLA"] = df.get("ACHATS_HORS_REGION_MARCH", 0)
        df["ECART_NOTIF"] = df.get("ECART", 0)

        # --------------------------
        # Connexion DB
        # --------------------------
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # --------------------------
        # Chargement NIU
        # --------------------------
        cur.execute("""
            SELECT niu, raison_sociale, sigle, activite,
                   regime, centre, etat, telephone
            FROM niu
        """)
        df_niu = pd.DataFrame(cur.fetchall())

        if not df_niu.empty:
            df_niu.columns = df_niu.columns.str.upper()
            df = df.merge(df_niu, on="NIU", how="left")

        # --------------------------
        # Chargement UG
        # --------------------------
        cur.execute("""
            SELECT centre, cdif, crif, cdia, cria,
                   acdi, acri, ville, directeur, regional
            FROM ug
        """)
        df_ug = pd.DataFrame(cur.fetchall())

        if not df_ug.empty:
            df_ug.columns = df_ug.columns.str.upper()
            df = df.merge(df_ug, on="centre", how="left")

        # --------------------------
        # Extraction IDA / IDB
        # --------------------------
        try:
            base = os.path.basename(fichier)
            bloc = base.replace("exploiter_", "").split("_")[0]
            ida, idb = bloc.split("X")
            IDA, IDB = int(ida), int(idb)
        except Exception:
            raise ValueError(f"Nom fichier invalide : {fichier}")

        # --------------------------
        # Sources PostgreSQL
        # --------------------------
        cur.execute("""
            SELECT * FROM sources_lac
            WHERE id IN (%s, %s)
        """, (IDA, IDB))

        rows = cur.fetchall()
        sources = {row["id"]: row for row in rows}

        if IDA not in sources or IDB not in sources:
            raise ValueError("Sources introuvables")

        source_a = sources[IDA]
        source_b = sources[IDB]

        # --------------------------
        # Enrichissement
        # --------------------------
        df["SOURCE_A"] = source_a["intitule_source"]
        df["SOURCE_B"] = source_b["intitule_source"]
        df["PERIODE_A"] = source_a["annee"]
        df["PERIODE_B"] = source_b["annee"]
        df["PROVENANCE_A"] = source_a["fournisseur"]
        df["PROVENANCE_B"] = source_b["fournisseur"]

        cur.close()
        conn.close()

        # --------------------------
        # Paramètres métier
        # --------------------------
        annee = datetime.now().year

        df["PERIODE"] = str(annee)
        df["REF_NOTIF"] = f"UTTAD-{annee}-{historique_id:05d}"
        df["RISQUE"] = risque
        df["AXE"] = axe
        df["MATIERE"] = matiere
        df["LISTE_IMPOTS"] = str(impots_inclus)
        df["AUTRE_TAXE"] = autre_taxe

        # --------------------------
        # Calcul BASE
        # --------------------------
        df["MARGE_TAUX"] = 20
        df["MARGE"] = df["ECART_NOTIF"] * 0.2
        df["BASE"] = df["ECART_NOTIF"] + df["MARGE"]

        # ===============================
        # FONCTION INIT COLONNES
        # ===============================
        def init_colonnes(prefix):
            df[f"{prefix}_BASE"] = 0
            df[f"{prefix}_TAUX"] = 0
            df[f"{prefix}_PRINCI"] = 0
            df[f"{prefix}_PENAL"] = 0
            df[f"{prefix}_TOTAL"] = 0

        # ===============================
        # TVA
        # ===============================
        init_colonnes("TVA")
        if "TVA" in impots_inclus:
            df["TVA_BASE"] = df["BASE"]
            df["TVA_TAUX"] = 19.25
            df["TVA_PRINCI"] = df["BASE"] * 0.1925
            df["TVA_PENAL"] = df["TVA_PRINCI"] * 0.3
            df["TVA_TOTAL"] = df["TVA_PRINCI"] + df["TVA_PENAL"]

        # ===============================
        # IS
        # ===============================
        init_colonnes("IS")
        if "IS" in impots_inclus:
            df["IS_BASE"] = np.where(df["NIU"].astype(str).str.startswith("P"), 0, df["BASE"])
            df["IS_TAUX"] = np.where(df["CENTRE"].astype(str).str.startswith("DGE"), 33, 27.5)
            df["IS_PRINCI"] = df["IS_BASE"] * df["IS_TAUX"] / 100
            df["IS_PENAL"] = df["IS_PRINCI"] * 0.3
            df["IS_TOTAL"] = df["IS_PRINCI"] + df["IS_PENAL"]

        # ===============================
        # IRPP
        # ===============================
        init_colonnes("IRPP")
        if "IRPP" in impots_inclus:
            base_irpp = np.where(df["NIU"].astype(str).str.startswith("M"), 0, df["BASE"])
            SNT = np.maximum(base_irpp - 500000, 0)

            IRPP_VAL = np.select(
                [
                    SNT <= 0,
                    SNT <= 2000000,
                    SNT <= 3000000,
                    SNT <= 5000000,
                    SNT > 5000000
                ],
                [
                    0,
                    SNT * 0.10,
                    2000000*0.10 + (SNT-2000000)*0.15,
                    2000000*0.10 + 1000000*0.15 + (SNT-3000000)*0.25,
                    2000000*0.10 + 1000000*0.15 + 2000000*0.25 + (SNT-5000000)*0.35
                ]
            )

            df["IRPP_PRINCI"] = IRPP_VAL
            df["IRPP_PENAL"] = IRPP_VAL * 0.3
            df["IRPP_TOTAL"] = df["IRPP_PRINCI"] + df["IRPP_PENAL"]

        # ===============================
        # IRCM
        # ===============================
        init_colonnes("IRCM")
        if "IRCM" in impots_inclus:
            df["IRCM_BASE"] = df["BASE"] - df["IS_PRINCI"] - df["IRPP_PRINCI"]
            df["IRCM_TAUX"] = 16.5
            df["IRCM_PRINCI"] = df["IRCM_BASE"] * 0.165
            df["IRCM_PENAL"] = df["IRCM_PRINCI"] * 0.3
            df["IRCM_TOTAL"] = df["IRCM_PRINCI"] + df["IRCM_PENAL"]

        # ===============================
        # AUTRE TAXE
        # ===============================
        if "Autre_taxe" in impots_inclus and autre_taxe:
            prefix = autre_taxe.upper()
            init_colonnes(prefix)

            df[f"{prefix}_BASE"] = df["BASE"]
            df[f"{prefix}_TAUX"] = 5
            df[f"{prefix}_PRINCI"] = df["BASE"] * 0.05
            df[f"{prefix}_PENAL"] = df[f"{prefix}_PRINCI"] * 0.3
            df[f"{prefix}_TOTAL"] = df[f"{prefix}_PRINCI"] + df[f"{prefix}_PENAL"]

        # --------------------------
        # Totaux
        # --------------------------
        df["TAX_PRINCI"] = df.filter(like="_PRINCI").sum(axis=1)
        df["TAX_PENAL"] = df.filter(like="_PENAL").sum(axis=1)
        df["TAX_TOTAL"] = df["TAX_PRINCI"] + df["TAX_PENAL"]

        # --------------------------
        # Titres
        # --------------------------
        df["TITRE"] = np.where(df["NIU"].astype(str).str.startswith("M"),
                              "Monsieur/Madame le Directeur de",
                              "Monsieur/Madame")

        df["APPEL"] = np.where(df["NIU"].astype(str).str.startswith("M"),
                              "Monsieur/Madame le Directeur",
                              "Monsieur/Madame")

        # --------------------------
        # Sauvegarde
        # --------------------------
        nouveau_nom = fichier.replace("exploiter", "Output")
        chemin_sortie = os.path.join(SORTIE_DIR, nouveau_nom)

        df.to_excel(chemin_sortie, index=False)

        return {
            "message": "Restitution générée avec succès.",
            "fichier_genere": nouveau_nom
        }

    except Exception as e:
        return {
            "message": f"Erreur : {str(e)}",
            "fichier_genere": None
        }