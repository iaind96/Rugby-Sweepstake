from flask import Blueprint, redirect, flash, render_template, url_for
from flask_login import current_user, login_required

from sweepstake import db
from sweepstake.models import User
from sweepstake.forms import UpdateInfoForm


bp = Blueprint("user", __name__, url_prefix="/user")


@bp.route("/<username>")
def user(username):
    #TODO: display user score
    user = User.query.filter_by(username=username).first_or_404()
    predictions = user.predictions
    return render_template("user/user.html", user=user, predictions=predictions)


@bp.route("/update", methods=("GET", "POST"))
@login_required
def update_info():
    user = current_user
    form = UpdateInfoForm(username=user.username, email=user.email, bio=user.bio)

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        bio = form.bio.data
        error = None

        if User.query.filter_by(username=username).first() is not None and username != user.username:
            error = f"Username {username} is already taken"
        if User.query.filter_by(email=email).first() is not None and email != user.email:
            error = f"Email {email} is already registered to another user"

        if error is None:
            user.username = username
            user.email = email
            user.bio = bio
            db.session.commit()
            return redirect(url_for("user.user", username=username))

        flash(error)

    return render_template("user/update.html", form=form, user=user)