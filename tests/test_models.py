import pytest
import datetime as dt

from sweepstake.models import User, Prediction, Match


class TestUser:

    def test_user_password_setting_and_checking(self):
        user = User(username="test")
        user.set_password("password")
        assert user.password_hash is not None
        assert user.check_password("password")
        assert not user.check_password("wrongpassword")

    def test_get_score(self, monkeypatch):
        def fake_calculate_score_1():
            return 5

        def fake_calculate_score_2():
            return 10

        def fake_calculate_score_3():
            return None

        user = User()
        prediction_1 = Prediction(user=user)
        monkeypatch.setattr(prediction_1, "calculate_score", fake_calculate_score_1)
        prediction_2 = Prediction(user=user)
        monkeypatch.setattr(prediction_2, "calculate_score", fake_calculate_score_2)
        prediction_3 = Prediction(user=user)
        monkeypatch.setattr(prediction_3, "calculate_score", fake_calculate_score_3)

        assert user.get_score() == 15

    def test_get_score_no_results(self, monkeypatch):
        def fake_calculate_score_1():
            return None

        user = User()
        prediction_1 = Prediction(user=user)
        monkeypatch.setattr(prediction_1, "calculate_score", fake_calculate_score_1)

        assert user.get_score() == 0


class TestMatch:

    def test_print_details(self):
        match = Match(date=dt.datetime(2020, 1, 1, 14, 0), venue="test venue")
        assert match.print_details() == "14:00, Jan 01 2020 at test venue"

        match = Match()
        assert match.print_details() is None

    @pytest.mark.parametrize(("team_a", "team_b", "id"), (
            ("abc", "def", "abc_def"),
            ("def", "abc", "abc_def"),
            ("Abc", "def", "Abc_def"),
            ("Def", "abc", "Def_abc")
    ))
    def test_unique_id(self, team_a, team_b, id):
        match = Match(team_a=team_a, team_b=team_b)
        assert match.unique_id() == id

    @pytest.mark.parametrize(("team_a", "team_b"), (
            ("Team A", "Team B"),
            ("Team B", "Team A")
    ))
    def test_check_exists(self, app, team_a, team_b):
        match = Match(team_a=team_a, team_b=team_b)
        with app.app_context():
            assert match.check_exists()

    @pytest.mark.parametrize(("team_a_score", "team_b_score", "result"), (
            (10, 0, "team_a"),
            (0, 10, "team_b"),
            (10, 10, "tie"),
            (None, None, None)
    ))
    def test_get_result(self, team_a_score, team_b_score, result):
        match = Match(team_a_score=team_a_score, team_b_score=team_b_score)
        assert match.get_result() == result

    @pytest.mark.parametrize(("team_a_score", "team_b_score", "result"), (
            (None, None, False),
            (10, None, False),
            (None, 10, False),
            (10, 10, True)
    ))
    def test_has_result(self, team_a_score, team_b_score, result):
        match = Match(team_a_score=team_a_score, team_b_score=team_b_score)
        assert match.has_result() is result

    @pytest.mark.parametrize(("team_a_score", "team_b_score", "result"), (
            (None, None, "-"),
            (10, 10, "10-10")
    ))
    def test_print_score(self, team_a_score, team_b_score, result):
        match = Match(team_a_score=team_b_score, team_b_score=team_b_score)
        assert match.print_score() == result


class TestPrediction:

    @pytest.mark.parametrize(("team_a_score", "team_b_score", "points"), (
            (50, 0, 0),     #incorrect result
            (0, 50, 5),     #correct result
            (7, 50, 10),    #team_a within 3pt
            (0, 43, 10),    #team_b within 3pt
            (7, 43, 15),    #both teams within 3pt
            (21, 49, 10),   #margin with 3pt
            (9, 41, 20),    #both teams and margin within 3pt
            (10, 50, 15),   #team_a correct
            (0, 40, 15),    #team b correct
            (10, 40, 50),   #correct score
    ))
    def test_calculate_score(self, team_a_score, team_b_score, points):
        match = Match(team_a="Team A", team_b="Team B", team_a_score=10, team_b_score=40)
        prediction = Prediction(team_a_score=team_a_score, team_b_score=team_b_score, match=match)
        assert prediction.calculate_score() == points

    def test_calculate_score_no_result(self):
        match = Match(team_a="Team A", team_b="Team B")
        prediction = Prediction(team_a_score=10, team_b_score=5, match=match)
        assert prediction.calculate_score() is None

    @pytest.mark.parametrize(("team_a_score", "team_b_score", "result"), (
            (10, 0, "team_a"),
            (0, 10, "team_b"),
            (10, 10, "tie")
    ))
    def test_get_prediction(self, team_a_score, team_b_score, result):
        prediction = Prediction(team_a_score=team_a_score, team_b_score=team_b_score)
        assert prediction.get_prediction() == result

    @pytest.mark.parametrize(("prediction", "actual", "points"), (
            (0, 10, 0),
            (7, 10, 5),
            (13, 10, 5),
            (10, 10, 10)
    ))
    def test_mark_score(self, prediction, actual, points):
        assert Prediction.mark_score(prediction, actual) == points

    @pytest.mark.parametrize(("prediction", "actual", "points"), (
            (0, 10, 0),
            (7, 10, 5),
            (13, 10, 5)
    ))
    def test_mark_score(self, prediction, actual, points):
        assert Prediction.mark_margin(prediction, actual) == points