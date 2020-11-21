import pytest
from flask_login import current_user

from sweepstake.models import User


class TestRegister:

    def test_register_render(self, client):
        assert client.get("auth/register").status_code == 200

    def test_register_functionality(self, client, app):
        response = client.post(
            "auth/register", data={"username": "a", "email": "a@flaskr.com",
                                   "password": "a", "password2": "a",
                                   "bio": "a bio"}
        )
        assert "http://localhost/auth/login" == response.headers["Location"]

        with app.app_context():
            user = User.query.filter_by(username="a").first()
            assert user is not None
            assert user.email == "a@flaskr.com"
            assert user.bio == "a bio"

    @pytest.mark.parametrize(("username", "email", "message"), (
            ("test", "new_email@flaskr.com", b"User test is already registered"),
            ("new", "test@flaskr.com", b"Email test@flaskr.com is already taken")
    ))
    def test_register_input_validation(self, client, username, email, message):
        response = client.post(
            "auth/register", data={"username": username, "email": email,
                                   "password": "password", "password2": "password"}
        )
        assert message in response.data


class TestLogin:

    def test_login_render(self, client):
        assert client.get("auth/login").status_code == 200

    def test_login_functionality(self, client, user):
        response = user.login()
        assert response.headers["Location"] == "http://localhost/"
        assert client.get("auth/login").headers["Location"] == "http://localhost/"

        with client:
            client.get("/")
            assert current_user.id == 1
            assert current_user.username == "test"

    def test_login_redirect(self, client, user):
        response = user.login(query_string={"next": "/1/update"})
        assert response.headers["Location"] == "http://localhost/1/update"

    @pytest.mark.parametrize(("username", "password", "message"), (
            ("a", "a", b"Incorrect username"),
            ("test", "a", b"Incorrect password")
    ))
    def test_login_input_validation(self, client, username, password, message):
        response = client.post(
            "auth/login", data={"username": username, "password": password}
        )
        assert message in response.data


class TestLogout:

    def test_logout(self, client, user):
        user.login()
        response = user.logout()
        assert response.headers["Location"] == "http://localhost/"

        with client:
            client.get("/")
            assert current_user.is_anonymous