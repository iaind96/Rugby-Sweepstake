import datetime as dt
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

from sweepstake import db


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    bio = db.Column(db.String(140), index=True)
    has_entered = db.Column(db.Boolean(), default=False)
    predictions = db.relationship("Prediction", backref="user", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_score(self):
        scores = [prediction.calculate_score() for prediction in self.predictions]
        return sum(filter(None, scores))

    def __repr__(self):
        return f"<User {self.username}>"


class Match(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    team_a = db.Column(db.String(20))
    team_b = db.Column(db.String(20))
    team_a_score = db.Column(db.Integer)
    team_b_score = db.Column(db.Integer)
    date = db.Column(db.DateTime, index=True)
    venue = db.Column(db.String(20))
    predictions = db.relationship("Prediction", backref="match", lazy="dynamic")

    def __str__(self):
        return f"{self.team_a} - {self.team_b}"

    def get_details(self):
        if self.date is None or self.venue is None:
            return None
        return f"{self.date.hour:d}:{self.date.minute:02d}, {self.date.strftime('%b %d %Y')} at {self.venue}"

    def check_exists(self):
        matches = Match.query.all()
        ids = [match.unique_id() for match in matches]
        new_id = self.unique_id()
        return new_id in ids

    def unique_id(self):
        return "_".join(sorted([self.team_a, self.team_b]))

    def get_result(self):
        if not self.has_result():
            return None

        if self.team_a_score > self.team_b_score:
            return "team_a"
        elif self.team_b_score > self.team_a_score:
            return "team_b"
        else:
            return "tie"

    def has_result(self):
        if self.team_a_score is not None and self.team_b_score is not None:
            return True
        else:
            return False

    def __repr__(self):
        return f"<Match {self.team_a} vs {self.team_b}>"


class Prediction(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey("match.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    team_a_score = db.Column(db.Integer)
    team_b_score = db.Column(db.Integer)

    def __str__(self):
        return f"{self.team_a_score} - {self.team_b_score}"

    def calculate_score(self):
        result = self.match.get_result()
        if result is None:
            return None

        prediction = self.get_prediction()
        score = 0

        if prediction == result:
            score += 5

            team_a_score_points = self.mark_score(self.team_a_score, self.match.team_a_score)
            team_b_score_points = self.mark_score(self.team_b_score, self.match.team_b_score)

            score += team_a_score_points
            score += team_b_score_points

            margin_actual = abs(self.match.team_a_score - self.match.team_b_score)
            margin_prediction = abs(self.team_a_score - self.team_b_score)

            margin_points = self.mark_score(margin_prediction, margin_actual)
            score += margin_points

            if team_a_score_points == 10 and team_b_score_points == 10:
                score += 15

        return score

    @staticmethod
    def mark_margin(prediction, actual):
        if abs(prediction - actual) <= 3:
            return 5
        else:
            return 0

    @staticmethod
    def mark_score(prediction, actual):
        if prediction == actual:
            return 10
        elif abs(prediction - actual) <= 3:
            return 5
        else:
            return 0

    def get_prediction(self):
        if self.team_a_score > self.team_b_score:
            return "team_a"
        elif self.team_b_score > self.team_a_score:
            return "team_b"
        else:
            return "tie"

    def __repr__(self):
        return f"<Prediction match: {self.match} by user: {self.user}>"