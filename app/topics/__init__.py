from flask import Blueprint

bp = Blueprint('topics', __name__)

from app.topics import routes
