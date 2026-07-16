import pytest

from quickParkFinder import create_app
from quickParkFinder.db import init_db


@pytest.fixture()
def app(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE": str(tmp_path / "test.sqlite"),
    })

    with app.app_context():
        init_db()

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def register(client):
    def _register(username="alice", password="secret123"):
        return client.post(
            "/auth/register/",
            data={"username": username, "password": password},
            follow_redirects=True,
        )
    return _register


@pytest.fixture()
def login(client, register):
    def _login(username="alice", password="secret123"):
        register(username, password)
        return client.post(
            "/auth/login/",
            data={"username": username, "password": password},
            follow_redirects=True,
        )
    return _login
