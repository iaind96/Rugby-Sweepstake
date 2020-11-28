from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import InputRequired
import datetime as dt

from sweepstake import db
from sweepstake.models import Match, Prediction, User
from sweepstake.forms import CreateMatchForm


bp = Blueprint("competition", __name__, url_prefix="/competition")


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    form = CreateMatchForm()

    if form.validate_on_submit():
        team_a = form.team_a.data
        team_b = form.team_b.data
        venue = form.venue.data
        date = dt.datetime.combine(form.date.data, form.time.data)
        match = Match(team_a=team_a, team_b=team_b, venue=venue, date=date)
        error = None

        if match.check_exists():
            error = f"Match {team_a} vs {team_b} is already in the database"

        if error is None:
            db.session.add(match)
            db.session.commit()
            return redirect(url_for("index"))

        flash(error)

    return render_template("competition/create.html", form=form)


@bp.route("/update/<int:id>", methods=("GET", "POST"))
@login_required
def update(id):
    match = Match.query.filter_by(id=id).first_or_404()

    class UpdateMatchForm(FlaskForm):
        team_a_score = IntegerField(f"{match.team_a}", validators=[InputRequired()])
        team_b_score = IntegerField(f"{match.team_b}", validators=[InputRequired()])
        submit = SubmitField("Enter Scores")

    form = UpdateMatchForm()

    if form.validate_on_submit():
        match.team_a_score = form.team_a_score.data
        match.team_b_score = form.team_b_score.data
        db.session.commit()

        return redirect(url_for("index"))

    return render_template("competition/update.html", match=match, form=form)


@bp.route("/match_list")
def match_list():
    matches = Match.query.all()
    return render_template("competition/match_list.html", matches=matches)


@bp.route("/<int:id>")
def match(id):
    match = Match.query.filter_by(id=id).first_or_404()
    predictions = Prediction.query.filter_by(match_id=match.id).all()
    return render_template("competition/match.html", match=match, predictions=predictions)


@bp.route("/enter", methods=("GET", "POST"))
@login_required
def enter():

    if current_user.has_entered:
        return redirect(url_for("index"))

    class EnterCompetitionForm(FlaskForm):
        submit = SubmitField("Enter")

    matches = Match.query.all()
    match_fields = []
    for match in matches:
        setattr(EnterCompetitionForm, f"{match.id}_team_a_score",
                IntegerField(f"{match.team_a}", validators=[InputRequired()]))
        setattr(EnterCompetitionForm, f"{match.id}_team_b_score",
                IntegerField(f"{match.team_b}", validators=[InputRequired()]))
        match_fields.append((f"{match.id}_team_a_score", f"{match.id}_team_b_score"))

    form = EnterCompetitionForm()

    if form.validate_on_submit():
        for match in matches:
            team_a_score = getattr(form, f"{match.id}_team_a_score").data
            team_b_score = getattr(form, f"{match.id}_team_b_score").data
            prediction = Prediction(team_a_score=team_a_score, team_b_score=team_b_score,
                                    match_id=match.id, user_id=current_user.id)
            db.session.add(prediction)
        current_user.has_entered = True
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("competition/enter.html", form=form, match_fields=match_fields)