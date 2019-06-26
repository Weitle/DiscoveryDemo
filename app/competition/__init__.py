from flask import Blueprint

competition = Blueprint("competition", __name__, url_prefix="/competition")

from . import views