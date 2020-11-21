from flask import Blueprint, render_template

from sweepstake.models import Match


bp = Blueprint("home", __name__)


@bp.route("/")
def home():
    matches = Match.query.all()
    return render_template("home/home.html", matches=matches)