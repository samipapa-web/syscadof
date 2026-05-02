import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ==========================
# Gestion des Templates
# ==========================
TEMPLATES_DIR = os.path.join("data", "Templates")


def list_templates():
    """Renvoie la liste des fichiers dans data/Templates"""
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    list_templates.directory = TEMPLATES_DIR  # pour téléchargement
    return [f for f in os.listdir(TEMPLATES_DIR) if os.path.isfile(os.path.join(TEMPLATES_DIR, f))]

def save_template(filename, file):
    """Enregistre ou remplace un fichier template"""
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    path = os.path.join(TEMPLATES_DIR, filename)
    file.save(path)
    return {"success": True, "message": f"Template '{filename}' mis à jour avec succès"}

# ==========================
# Gestion des Fichiers
# ==========================
FICHIERS_DIR = os.path.join("data", "Fichier")

def list_fichiers():
    """Renvoie la liste des fichiers dans data/Fichier"""
    os.makedirs(FICHIERS_DIR, exist_ok=True)
    list_fichiers.directory = FICHIERS_DIR
    return [f for f in os.listdir(FICHIERS_DIR) if os.path.isfile(os.path.join(FICHIERS_DIR, f))]

def save_fichier(filename, file):
    """Enregistre ou remplace un fichier référentiel"""
    os.makedirs(FICHIERS_DIR, exist_ok=True)
    path = os.path.join(FICHIERS_DIR, filename)
    file.save(path)
    return {"success": True, "message": f"Référentiel '{filename}' mis à jour avec succès"}