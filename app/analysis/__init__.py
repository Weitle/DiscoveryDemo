from flask import Blueprint

analysis = Blueprint("analysis", __name__, url_prefix="/analysis")

from . import views