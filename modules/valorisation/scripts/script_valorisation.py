import os
import pandas as pd
import numpy as np
import traceback
import logging
from datetime import datetime
from database import get_connection
from config import SORTIE_DIR


# =========================================================
# LOGGING
# =========================================================
logger = logging.getLogger("valorisation")

if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )


# =========================================================
# UTILS
# =========================================================
def normalize_columns(df):
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.upper()
        .str.replace(" ", "_")
        .str.replace("É", "E")
        .str.replace("È", "E")
        .str.replace("Ê", "E")
        .str.replace("À", "A")
    )
    return df


def to_numeric_safe(series):
    return pd.to_numeric(series, errors="coerce").fillna(0)


def init_tax_columns(df, prefix):
    for col in ["BASE", "TAUX", "PRINCI", "PENAL", "TOTAL"]:
        df[f"{prefix}_{col}"] = 0


# =========================================================
# TRAITEMENT PRINCIPAL
# =========================================================
def traitement_valorisation(
    fichier,
    matiere,
    risque,
    axe,
    historique_id,
    impots_inclus,
    autre_taxe=""
):

    conn = None
    cur = None

    try:
        logger.info(f"Début traitement : {fichier}")

        # =====================================================
        # FICHIER
        # =====================================================
        os.makedirs(SORTIE_DIR, exist_ok=True)
        chemin_source = os.path.join(SORTIE_DIR, fichier)

        if not os.path.exists(chemin_source):
            raise FileNotFoundError(f"Fichier introuvable : {fichier}")

        df = pd.read_excel(chemin_source)
        df = normalize_columns(df)

        #-------------------------------------------------------------------
        # Suppression de RAISON_SOCIALE si existant,
        # car cette variable sera importee depuis la base NIU
        # pour conserver l'orthographe utilise pour publipostage
        #-------------------------------------------------------------------
        df.drop(columns=["RAISON_SOCIALE"], errors="ignore", inplace=True)

        logger.info(f"Lignes: {df.shape[0]} | Colonnes: {df.shape[1]}")

        # =====================================================
        # COLONNES METIER
        # =====================================================
        df["VAL_RECOUP"] = to_numeric_safe(df.get("TOTAL_GENERAL", 0))
        df["VAL_DECLA"] = to_numeric_safe(df.get("ACHATS_HORS_REGION_MARCH", 0))
        df["ECART_NOTIF"] = to_numeric_safe(df.get("ECART", 0))

        # Nettoyage clés
        if "NIU" in df.columns:
            df["NIU"] = df["NIU"].astype(str).str.strip()

        if "CENTRE" in df.columns:
            df["CENTRE"] = df["CENTRE"].astype(str).str.strip()

        # =====================================================
        # DB
        # =====================================================
        conn = get_connection()
        cur = conn.cursor()

        # =====================================================
        # CROISEMENT AVEC BASE DES NIU
        # =====================================================
        if "NIU" in df.columns:

            nius = df["NIU"].dropna().unique().tolist()

            if nius:
                logger.info(f"Chargement NIU filtré ({len(nius)})")

                cur.execute("""
                    SELECT niu, raison_sociale, sigle, activite,
                           regime, centre, etat, telephone
                    FROM niu
                    WHERE niu = ANY(%s)
                """, (nius,))

                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()

                df_niu = pd.DataFrame(rows, columns=columns)

                if not df_niu.empty:
                    df_niu = normalize_columns(df_niu)
                    df_niu["NIU"] = df_niu["NIU"].astype(str).str.strip()

                    df = df.merge(df_niu, on="NIU", how="left")

        # =====================================================
        # CROISEMENT AVEC BASE DES UG
        # =====================================================
        if "CENTRE" in df.columns:

            centres = df["CENTRE"].dropna().unique().tolist()

            if centres:
                logger.info(f"Chargement UG filtré ({len(centres)})")

                cur.execute("""
                    SELECT centre, cdif, crif, cdia, cria,
                           acdi, acri, ville, directeur, regional
                    FROM ug
                    WHERE centre = ANY(%s)
                """, (centres,))

                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()

                df_ug = pd.DataFrame(rows, columns=columns)

                if not df_ug.empty:
                    df_ug = normalize_columns(df_ug)
                    df_ug["CENTRE"] = df_ug["CENTRE"].astype(str).str.strip()

                    df = df.merge(df_ug, on="CENTRE", how="left")

        # =====================================================
        # SOURCES LAC
        # =====================================================
        base = os.path.basename(fichier)
        bloc = base.replace("exploiter_", "").split("_")[0]

        try:
            ida, idb = bloc.split("X")
            IDA, IDB = int(ida), int(idb)
        except:
            raise ValueError(f"Nom fichier invalide : {fichier}")

        cur.execute("""
            SELECT *
            FROM sources_lac
            WHERE id = ANY(%s)
        """, ([IDA, IDB],))

        columns = [desc[0] for desc in cur.description]
        rows = [dict(zip(columns, r)) for r in cur.fetchall()]

        sources = {r["id"]: r for r in rows}

        source_a = sources.get(IDA)
        source_b = sources.get(IDB)

        if not source_a or not source_b:
            raise ValueError("Sources introuvables")

        df["SOURCE_A"] = source_a.get("intitule_source", "")
        df["SOURCE_B"] = source_b.get("intitule_source", "")
        df["PERIODE_A"] = source_a.get("annee", "")
        df["PERIODE_B"] = source_b.get("annee", "")
        df["PROVENANCE_A"] = source_a.get("fournisseur", "")
        df["PROVENANCE_B"] = source_b.get("fournisseur", "")

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
                              
        # =====================================================
        # SAUVEGARDE
        # =====================================================
        nouveau_nom = fichier.replace("exploiter", "Output")
        chemin_sortie = os.path.join(SORTIE_DIR, nouveau_nom)

        df.to_excel(chemin_sortie, index=False)

        logger.info(f"Fichier généré : {nouveau_nom}")

        return {
            "message": "Restitution générée avec succès.",
            "fichier_genere": nouveau_nom
        }

    except Exception as e:
        logger.error("Erreur traitement", exc_info=True)

        return {
            "message": str(e),
            "trace": traceback.format_exc(),
            "fichier_genere": None
        }

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
