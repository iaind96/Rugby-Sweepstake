from flask import Blueprint, render_template

from sweepstake.models import Match, User


bp = Blueprint("home", __name__)


@bp.route("/")
def home():
    #TODO: rank users by score
    #TODO: add links to update each match with scores
    matches = Match.query.all()
    users = User.query.filter_by(has_entered=True).all()
    return render_template("home/home.html", matches=matches, users=users)