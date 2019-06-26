from flask import render_template
from . import competition

@competition.route("/")
@competition.route("/index")
def index():
    return render_template("competition/index.html")