from flask import Blueprint, render_template

from sweepstake.models import Match, User


bp = Blueprint("home", __name__)


@bp.route("/")
def home():
    #TODO: rank users by score
    #TODO: add links to update each match with scores
    users = User.query.filter_by(has_entered=True).all()

    scores = [(user, user.get_score()) for user in users]
    scores = sorted(scores, key=lambda x: x[1])

    return render_template("home/home.html", scores=scores)