# modules/traitement/services.py
#--------------------------------------------------------

import subprocess
import sys
import os


def execute_script(chemin_script, source_lac_id, base_dir):
    """
    Exécute un script Python externe (subprocess)
    avec injection de BASE_DIR et source_lac_id
    """

    if not os.path.exists(chemin_script):
        raise FileNotFoundError("Script introuvable")

    result = subprocess.run(
        [sys.executable, chemin_script],
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "source_lac_id": str(source_lac_id),
            "BASE_DIR": base_dir  # 🔥 injection critique
        }
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return result.stdout.strip()