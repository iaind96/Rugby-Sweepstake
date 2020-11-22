import pytest

from sweepstake.forms import LoginForm, RegisterForm, UpdateInfoForm, CreateMatchForm


@pytest.mark.parametrize(("username", "password"), (
        ("", "test"),
        ("test", "")
))
def test_login_form_validation(app, username, password):
    with app.app_context():
        form = LoginForm()
        form.username.data = username
        form.password.data = password
        assert not form.validate()

@pytest.mark.parametrize(("username", "email", "password", "password2"), (
        ("", "test@flaskr.com", "test", "test"),
        ("test", "", "test", "test"),
        ("test", "test", "test", "test"),
        ("test", "test@flaskr.com", "", "test"),
        ("test", "test@flaskr.com", "test", ""),
        ("test", "test@flaskr.com", "test", "test2")
))
def test_register_form_validation(app, username, email, password, password2):
    with app.app_context():
        form = RegisterForm()
        form.username.data = username
        form.email.data = email
        form.password.data = password
        form.password2.data = password2
        assert not form.validate()


@pytest.mark.parametrize(("username", "email"), (
        ("", "test@flaskr.com"),
        ("test", ""),
        ("test", "test"),
))
def test_update_info_form_validation(app, username, email):
    with app.app_context():
        form = UpdateInfoForm()
        form.username.data = username
        form.email.data = email
        assert not form.validate()


@pytest.mark.parametrize(("team_a", "team_b"), (
        ("", "test b"),
        ("test a", ""),
        ("test a", "test a")
))
def test_create_match_form_validation(app, team_a, team_b):
    with app.app_context():
        form = CreateMatchForm()
        form.team_a.data = team_a
        form.team_b.data = team_b
        # form.date.data = "01/01/2020"
        # form.time.data = "14:00"
        assert not form.validate()