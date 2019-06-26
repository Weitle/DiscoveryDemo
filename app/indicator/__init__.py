from flask import Blueprint

indicator = Blueprint("indicator", __name__, url_prefix="/indicator")

from . import views