def test_parking_requires_login(client):
    response = client.get("/parking/", follow_redirects=True)
    assert b"Log In" in response.data


def test_parking_form_validation_requires_location(client, login):
    login()
    response = client.post(
        "/parking/",
        data={"location": "", "level": "2", "row": "A", "notes": "Near elevator"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Location is required." in response.data


def test_parking_rejects_overlong_location(client, login):
    login()
    response = client.post(
        "/parking/",
        data={"location": "x" * 201, "level": "", "row": "", "notes": ""},
        follow_redirects=True,
    )
    assert b"Location is too long." in response.data


def test_full_parking_session_workflow(client, login):
    login()
    response = client.post(
        "/parking/",
        data={"location": "Garage B", "level": "3", "row": "C", "landmark": "Blue pillar", "notes": "Near stairs"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Garage B" in response.data
    assert b"3" in response.data
    assert b"C" in response.data
    assert b"Blue pillar" in response.data
    assert b"Near stairs" in response.data

def test_parking_confirmation_shows_timestamp(client,login):
    login()
    response = client.post(
        "/parking/",
        data={"location":"Garage D", "level":"", "row":"", "notes":""},
        follow_redirects=True,
    )
    assert b"Saved at:" in response.data

def test_parking_escapes_html_in_notes(client, login):
    login()
    client.post(
        "/parking/",
        data={"location": "Garage C", "level": "", "row": "", "notes": "<script>alert(1)</script>"},
    )
    response = client.get("/quickpark/")
    assert b"<script>" not in response.data
    assert b"&lt;script&gt;" in response.data
