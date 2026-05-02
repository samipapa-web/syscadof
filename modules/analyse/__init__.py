from flask import Blueprint

analyse_bp = Blueprint(
    'analyse', __name__,
    template_folder='templates',
    static_folder='static'
)

from . import routes, services