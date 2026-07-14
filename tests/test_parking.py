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


def test_parking_form_validation_requires_location(client):
    response = client.post(
        "/parking/",
        data={"location": "", "level": "2", "row": "A", "notes": "Near elevator"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    print("Parking validation returned HTTP 200")
    assert b"Location is required." in response.data
    print("Parking validation message appeared")


def test_full_parking_session_workflow(client):
    response = client.post(
        "/parking/",
        data={"location": "Garage B", "level": "3", "row": "C", "notes": "Near stairs"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    print("Parking record created successfully")
    assert b"Garage B" in response.data
    assert b"3" in response.data
    assert b"Near stairs" in response.data
    print("Parking record displayed after save")
