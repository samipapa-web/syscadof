#
# modules\valorisation\insert_scripts.py
#-------------------------------------------------------

import os

def list_scripts(scripts_dir):
    scripts = []
    if os.path.exists(scripts_dir):
        for f in os.listdir(scripts_dir):
            if f.endswith(".py"):
                scripts.append({"id": f, "titre": f.replace(".py", ""), "auteur": "Admin"})
    return scripts

def load_script(scripts_dir, script_name):
    script_path = os.path.join(scripts_dir, script_name)
    if not os.path.exists(script_path):
        return "", False, "Script introuvable"
    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content, True, None

def save_script(scripts_dir, titre, contenu):
    if not os.path.exists(scripts_dir):
        os.makedirs(scripts_dir)
    filename = f"{titre}.py"
    path = os.path.join(scripts_dir, filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(contenu)
        return True, f"Script sauvegardé : {filename}", None
    except Exception as e:
        return False, "", str(e)