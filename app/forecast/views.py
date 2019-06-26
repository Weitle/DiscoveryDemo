from flask import render_template
from . import forecast

@forecast.route("/")
@forecast.route("/index")
def index():
    return render_template("forecast/index.html")