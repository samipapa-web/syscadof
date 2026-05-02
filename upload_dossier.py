# ========================================
# upload_dossier.py executable sur Render Shell
# ========================================

import os
import shutil
import config


# =========================================================
# COPIE UNIQUEMENT DES FICHIERS .docx
# =========================================================
def upload_all():
    source_dir = os.path.join(config.BASE_DIR, "data", "Templates")
    destination_dir = os.path.join(config.DATA_DIR, "Templates")

    print("=======================================")
    print("📦 COPIE UNIQUEMENT DES FICHIERS DOCX")
    print("=======================================")
    print(f"📂 Source : {source_dir}")
    print(f"📁 Destination : {destination_dir}")

    try:
        if not os.path.exists(source_dir):
            raise FileNotFoundError(f"❌ Source introuvable : {source_dir}")

        os.makedirs(destination_dir, exist_ok=True)

        copied_files = 0

        # Parcours récursif
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.lower().endswith(".docx"):
                    src_file = os.path.join(root, file)

                    # recréer la structure des sous-dossiers
                    rel_path = os.path.relpath(root, source_dir)
                    dest_folder = os.path.join(destination_dir, rel_path)
                    os.makedirs(dest_folder, exist_ok=True)

                    dest_file = os.path.join(dest_folder, file)

                    shutil.copy2(src_file, dest_file)
                    copied_files += 1

        print(f"✅ Copie terminée : {copied_files} fichiers .docx copiés")

    except Exception as e:
        print(f"❌ Erreur copie fichiers DOCX : {e}")


# =========================================================
# LANCEMENT
# =========================================================
def copy_dossier():
    upload_all()


# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":
    print("🚀 Copie en cours...")
    copy_dossier()