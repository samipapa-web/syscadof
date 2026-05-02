from flask import Blueprint
from .services import init_valorisation_table

valorisation_bp = Blueprint(
    "valorisation",
    __name__,
    url_prefix="/valorisation",
    template_folder="templates"
)

# IMPORTANT : appel après création du blueprint
init_valorisation_table()

from . import routes
