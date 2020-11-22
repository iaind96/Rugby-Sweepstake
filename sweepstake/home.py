from flask import Blueprint, render_template

from sweepstake.models import Match, User


bp = Blueprint("home", __name__)


@bp.route("/")
def home():
    matches = Match.query.all()
    users = User.query.filter_by(has_entered=True).all()
    return render_template("home/home.html", matches=matches, users=users)