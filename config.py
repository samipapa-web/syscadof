# config.py
# ========================================
import os

# =========================================================
# BASE_DIR et DATA_DIR
# =========================================================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# =========================================================
# DATA_DIR dynamique (local vs production)
# =========================================================
DATA_DIR = os.getenv("DATA_DIR", os.path.join(BASE_DIR, "data"))

# Sous-dossiers
DATA_LAC_DIR = os.path.join(DATA_DIR, "LAC")
DATA_CLEAN_DIR = os.path.join(DATA_DIR, "clean")
SORTIE_DIR = os.path.join(DATA_DIR, "Sortie")
TEMPLATES_DIR = os.path.join(DATA_DIR, "Templates")

#Fichier excel de references
REF_PATH = os.path.join(BASE_DIR, "data", "Templates", "REFERENCES.xlsx")


# Scripts des modules
APUR_SCRIPT_DIR = os.path.join(BASE_DIR, "modules", "traitement", "scripts")
ANAL_SCRIPT_DIR = os.path.join(BASE_DIR, "modules", "analyse", "scripts")
VALO_SCRIPT_DIR = os.path.join(BASE_DIR, "modules", "valorisation", "scripts")
NOTI_SCRIPT_DIR = os.path.join(BASE_DIR, "modules", "notification", "scripts")



# =========================================================
# Création des dossiers si inexistants
# =========================================================

for folder in [DATA_LAC_DIR, DATA_CLEAN_DIR, TEMPLATES_DIR, SORTIE_DIR]:
    try:
        os.makedirs(folder, exist_ok=True)
    except PermissionError:
        print(f"⚠️ Impossible de créer le dossier {folder}, vérifiez les permissions.")
    

# =========================================================
# Paramètres généraux
# =========================================================
ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls", "txt"}
VALID_TEMPORALITES = ["Stock", "Flux annuel", "Flux mensuel"]

# =========================================================
# Débogage Render : afficher les chemins
# =========================================================
print(f"DATA_DIR = {DATA_DIR}")
print(f"DATA_LAC_DIR = {DATA_LAC_DIR}")
print(f"DATA_CLEAN_DIR = {DATA_CLEAN_DIR}")
print(f"SORTIE_DIR = {SORTIE_DIR}")