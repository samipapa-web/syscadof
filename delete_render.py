# ========================================
# delete_render.py executable sur Render Shell
# ========================================

import os
import config


# =========================================================
# SUPPRESSION DES FICHIERS "exploiter*"
# =========================================================
def delete_files():
    target_dir = config.DATA_DIR

    print("=======================================")
    print("🧹 SUPPRESSION DES FICHIERS 'exploiter*'")
    print("=======================================")
    print(f"📂 Dossier cible : {target_dir}")

    try:
        if not os.path.exists(target_dir):
            raise FileNotFoundError(f"❌ Dossier introuvable : {target_dir}")

        deleted_files = 0

        # Parcours récursif
        for root, dirs, files in os.walk(target_dir):
            for file in files:

                # 🔥 CONDITION PRINCIPALE
                if file.lower().startswith("exploiter"):

                    file_path = os.path.join(root, file)

                    try:
                        os.remove(file_path)
                        deleted_files += 1
                        print(f"🗑️ Supprimé : {file_path}")

                    except Exception as e:
                        print(f"⚠️ Erreur suppression {file_path} : {e}")

        print("---------------------------------------")
        print(f"✅ Suppression terminée : {deleted_files} fichier(s) supprimé(s)")

    except Exception as e:
        print(f"❌ Erreur globale : {e}")


# =========================================================
# LANCEMENT
# =========================================================
def run_delete():
    delete_files()


# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":
    print("🚀 Nettoyage en cours...")
    run_delete()