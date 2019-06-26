from flask import Blueprint

forecast = Blueprint("forecast", __name__, url_prefix="/")

from . import views