import pytest

from quickParkFinder import create_app
from quickParkFinder.db import init_db


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "test.sqlite"
    app = create_app({
        "TESTING": True,
        "DATABASE": str(db_path),
    })

    with app.app_context():
        init_db()

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_register_and_login_flow(client):
    response = client.post(
        "/auth/register/",
        data={"username": "alice", "password": "secret"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    print("Registration returned HTTP 200")
    assert b"Log In" in response.data
    print("Registration page rendered correctly")

    response = client.post(
        "/auth/login/",
        data={"username": "alice", "password": "secret"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    print("Login returned HTTP 200")
    assert b"Hello, World!" in response.data
    print("Login redirected to the expected page")
