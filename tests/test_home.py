

class TestHome:

    def test_navbar_render(self, client, user):
        response = client.get("/")
        assert b'href="/auth/login"' in response.data
        assert b'href="/auth/register"' in response.data
        assert b'href="/auth/logout' not in response.data

        user.login()
        response = client.get("/")
        assert b'href="/auth/logout' in response.data
        assert b'href="/user/test"' in response.data
        assert b'href="/auth/login"' not in response.data
        assert b'href="/auth/register"' not in response.data
        assert b'href="/competition/enter"' in response.data

        user.enter_competition()
        response = client.get("/")
        assert b'href="/competition/enter"' not in response.data

    def test_home_render(self, client, user):
        response = client.get("/")
        assert response.status_code == 200
        assert b'href="/competition/1"' in response.data
        assert b"Team A - Team B" in response.data

        user.login()
        response = client.get("/")
        assert b'href="/competition/create"' in response.data

        user.enter_competition()
        response = client.get("/")
        assert b'href="/user/test"' in response.data
        assert b': 0' in response.data