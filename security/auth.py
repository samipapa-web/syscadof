import os
import pandas as pd
from flask import session, redirect, render_template
from functools import wraps


roles_access = {}
USERS = {}


def load_roles_users(excel_path):

    global roles_access
    global USERS

    if not os.path.exists(excel_path):
        print("Fichier ROLES.xlsx introuvable")
        return

    # -----------------------------
    # CHARGEMENT DES ROLES
    # -----------------------------
    roles_df = pd.read_excel(excel_path, sheet_name="ROLES")

    for _, row in roles_df.iterrows():

        role = str(row["Role"]).strip()

        modules = {
            col: str(row[col]).strip().lower() == "oui"
            for col in roles_df.columns
            if col != "Role"
        }

        roles_access[role] = modules

    # -----------------------------
    # CHARGEMENT DES UTILISATEURS
    # -----------------------------
    users_df = pd.read_excel(excel_path, sheet_name="USERS")

    for _, row in users_df.iterrows():

        username = str(row["Utilisateur"]).strip()

        USERS[username] = {
            "password": str(row["Mot de passe"]).strip(),
            "role": str(row["Role"]).strip()
        }


# ======================================================
# DECORATEUR LOGIN
# ======================================================

def login_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if "user" not in session:
            return redirect("/login")

        return f(*args, **kwargs)

    return wrapper


# ======================================================
# DECORATEUR ROLE
# ======================================================

def access_required(module):

    def decorator(f):

        @wraps(f)
        def wrapper(*args, **kwargs):

            role = session.get("role")

            if not role:
                return redirect("/login")

            allowed = roles_access.get(role, {}).get(module, False)

            if not allowed:
                return render_template("403.html"), 403

            return f(*args, **kwargs)

        return wrapper

    return decorator