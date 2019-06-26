from flask import render_template

from . import indicator

@indicator.route("/income")
def income():
    return render_template("indicator/income.html")