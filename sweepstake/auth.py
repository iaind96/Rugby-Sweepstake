from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from sweepstake import db, login_manager
from sweepstake.models import User
from sweepstake.forms import LoginForm, RegisterForm


#TODO: implement admin user features

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        bio = form.bio.data
        user = User(username=username, email=email, bio=bio)
        user.set_password(password)
        error = None

        if User.query.filter_by(username=username).first() is not None and username:
            error = f"User {username} is already registered"
        if User.query.filter_by(email=email).first() is not None:
            error = f"Email {email} is already taken"

        if error is None:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html", form=form)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        error = None
        user = User.query.filter_by(username=username).first()

        if user is None:
            error = 'Incorrect username.'
        elif not user.check_password(password):
            error = 'Incorrect password.'

        if error is None:
            login_user(user)

            next_page = request.args.get("next")
            if not next_page or url_parse(next_page).netloc != "":
                next_page = url_for("index")
            return redirect(next_page)

        flash(error)

    return render_template('auth/login.html', form=form)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))