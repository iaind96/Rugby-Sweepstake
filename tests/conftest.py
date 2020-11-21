import os
import pytest
import datetime as dt

from sweepstake import create_app, db
from sweepstake.models import User, Match, Prediction


class ConfigTesting:
    # General Config
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or "secret_key"
    FLASK_APP = os.environ.get('FLASK_APP')
    FLASK_ENV = os.environ.get('FLASK_ENV')

    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture
def app():

    app = create_app(ConfigTesting)

    with app.app_context():
        db.create_all()
        populate_test_db(db)

    yield app

    with app.app_context():
        db.drop_all()


def populate_test_db(db):
    test_user_1 = User(
        username="test",
        email="test@flaskr.com",
        password_hash="pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f",
        bio="test bio"
    )
    test_user_2 = User(
        username="other",
        email="other@flaskr.com",
        password_hash="pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79",
        bio="other bio"
    )
    test_match_1 = Match(
        team_a="Team A",
        team_b="Team B",
        date=dt.datetime(2020, 1, 1, 14, 0),
        venue="test venue"
    )
    test_match_2 = Match(
        team_a="Team C",
        team_b="Team D"
    )
    test_prediction_1 = Prediction(
        match=test_match_1,
        user=test_user_2,
        team_a_score=10,
        team_b_score=20
    )

    rows = [test_user_1, test_user_2, test_match_1, test_match_2, test_prediction_1]
    for row in rows:
        db.session.add(row)
    db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


class UserActions:

    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test", query_string=None):
        return self._client.post(
            "auth/login",
            data={"username": username, "password": password},
            query_string=query_string
        )

    def logout(self):
        return self._client.get("auth/logout")

    def enter_competition(self):
        return self._client.post(
            "/competition/enter",
            data={
                "1_team_a_score": 10,
                "1_team_b_score": 20,
                "2_team_a_score": 0,
                "2_team_b_score": 10
            }
        )


@pytest.fixture
def user(client):
    return UserActions(client)
