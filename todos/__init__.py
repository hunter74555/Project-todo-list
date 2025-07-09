from flask import Blueprint

todos_bp = Blueprint('todos', __name__, template_folder='templates/todos')

from . import routes
