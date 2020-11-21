import pytest

from sweepstake.models import User


class TestUser:

    def test_user_render(self, client, user):
        response = client.get("user/test")
        assert response.status_code == 200
        assert b"test bio" in response.data
        assert b'href="/user/update"' not in response.data

        user.login()
        response = client.get("user/test")
        assert b'href="/user/update"' in response.data

        user.enter_competition()
        response = client.get("user/test")
        assert b'Team A - Team B' in response.data
        assert b'href="/competition/1"' in response.data


class TestUpdateInfo:

    def test_update_info_render(self, client, user):
        user.login()
        assert client.get("user/update").status_code == 200

    def test_update_info_login_required(self, client):
        response = client.get("user/update")
        assert "http://localhost/auth/login" in response.headers["Location"]

    @pytest.mark.parametrize(("username", "email"), (
            ("updated_username", "updated_email@flaskr.com"),
            ("test", "updated_email@flaskr.com"),
            ("updated_username", "test@flaskr.com")
    ))
    def test_update_info_functionality(self, client, app, user, username, email):
        user.login()
        response = client.post("user/update", data={
            "username": username,
            "email": email,
            "bio": "updated bio"
        })
        assert f"http://localhost/user/{username}" in response.headers["Location"]

        with app.app_context():
            user = User.query.filter_by(username=username).first()
            assert user is not None
            assert user.email == email
            assert user.bio == "updated bio"

    @pytest.mark.parametrize(("username", "email", "message"), (
            ("other", "update_email@flaskr.com", b"Username other is already taken"),
            ("update_username", "other@flaskr.com", b"Email other@flaskr.com is already registered to another user")
    ))
    def test_update_info_input_validation(self, client, user, username, email, message):
        user.login()
        response = client.post("user/update", data={
            "username": username, "email": email
        })
        assert message in response.data
