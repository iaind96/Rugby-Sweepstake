import pytest
import datetime as dt

from sweepstake.models import Match, User


class TestCreate:

    def test_create_match_render(self, client, user):
        user.login()
        assert client.get("/competition/create").status_code == 200

    def test_create_match_functionality(self, client, app, user):
        user.login()
        date = dt.datetime(2020, 1, 1, 14, 0)
        client.post("/competition/create", data={
            "team_a": "test team A",
            "team_b": "test team B",
            "date": "01/01/2020",
            "time": "14:00",
            "venue": "test venue"
        })

        with app.app_context():
            match = Match.query.filter_by(team_a="test team A").first()
            assert match is not None
            assert match.date == date
            assert match.venue == "test venue"

    def test_create_validate_input(self, client, app, user):
        user.login()
        response = client.post("/competition/create", data={
            "team_a": "Team A",
            "team_b": "Team B",
            "date": "01/01/2020",
            "time": "14:00"
        })
        assert b"Match Team A vs Team B is already in the database" in response.data


class TestUpdate:

    def test_update_render(self, client, user):
        user.login()
        response = client.get("/competition/update/1")
        assert response.status_code == 200
        assert b"Team A - Team B" in response.data
        assert b"Team A score" in response.data
        assert b"Team B score" in response.data

    def test_update_functionality(self, client, user, app):
        user.login()
        response = client.post("/competition/update/1", data={
            "team_a_score": 10,
            "team_b_score": 5
        })
        assert "http://localhost/" == response.headers["Location"]

        with app.app_context():
            match = Match.query.filter_by(id=1).first()
            assert match.team_a_score == 10
            assert match.team_b_score == 5


class TestEnter:

    def test_enter_render(self, client, user):
        user.login()
        assert client.get("/competition/enter").status_code == 200

    def test_enter_functionality(self, client, app, user):
        user.login()
        response = user.enter_competition()
        assert "http://localhost/" == response.headers["Location"]

        with app.app_context():
            user = User.query.filter_by(username="test").first()
            assert user.predictions[0].team_a_score == 10
            assert user.predictions[0].team_b_score == 20
            assert user.predictions[1].team_a_score == 0
            assert user.predictions[1].team_b_score == 10
            assert user.has_entered

        response = client.get("/competition/enter")
        assert response.headers["Location"] == "http://localhost/"


class TestMatch:

    def test_match_render(self, client, user):
        response = client.get("/competition/1")
        assert response.status_code == 200
        assert b'other' in response.data
        assert b'href="/user/other"' in response.data
        assert b'10 - 20' in response.data
        assert b'14:00, Jan 01 2020 at test venue' in response.data

        user.login()
        response = client.get("/competition/1")
        assert b'href="/competition/update/1"' in response.data


class TestMatchList:

    def test_match_list_render(self, client, user):
        response = client.get("/competition/match_list")
        assert response.status_code == 200
        assert b'href="/competition/1"' in response.data
        assert b"Team A - Team B" in response.data

        user.login()
        response = client.get("/competition/match_list")
        assert b'href="/competition/create"' in response.data