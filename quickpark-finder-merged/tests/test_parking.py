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


def test_parking_with_coordinates_shows_directions_link(client, login):
    login()
    response = client.post(
        "/parking/",
        data={
            "location": "Garage E",
            "level": "",
            "row": "",
            "notes": "",
            "latitude": "37.7749",
            "longitude": "-122.4194",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Get Directions" in response.data
    assert b"/directions" in response.data
    # the directions link itself must never embed the raw coordinates
    assert b"destination=37.7749" not in response.data

    # a later page load (no leftover form echo) must never show plaintext
    list_response = client.get("/quickpark/")
    assert b"37.7749" not in list_response.data


def test_parking_directions_link_redirects_to_maps_with_decrypted_coordinates(client, login):
    login()
    client.post(
        "/parking/",
        data={
            "location": "Garage E",
            "level": "", "row": "", "notes": "",
            "latitude": "37.7749",
            "longitude": "-122.4194",
        },
    )
    response = client.get("/quickpark/1/directions")
    assert response.status_code == 302
    assert response.location == "https://www.google.com/maps/dir/?api=1&destination=37.7749,-122.4194"


def test_directions_link_rejects_other_users_quickpark(client, login, register):
    login("alice", "secret123")
    client.post(
        "/parking/",
        data={
            "location": "Alice Garage",
            "level": "", "row": "", "notes": "",
            "latitude": "37.7749",
            "longitude": "-122.4194",
        },
    )
    client.get("/auth/logout/")

    register("bob", "secret123")
    client.post("/auth/login/", data={"username": "bob", "password": "secret123"}, follow_redirects=True)

    response = client.get("/quickpark/1/directions")
    assert response.status_code == 404


def test_parking_without_coordinates_omits_directions_link(client, login):
    login()
    response = client.post(
        "/parking/",
        data={"location": "Garage F", "level": "", "row": "", "notes": ""},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Get Directions" not in response.data


def test_parking_rejects_non_numeric_coordinates(client, login):
    login()
    response = client.post(
        "/parking/",
        data={
            "location": "Garage G",
            "level": "",
            "row": "",
            "notes": "",
            "latitude": "not-a-number",
            "longitude": "-122.4194",
        },
        follow_redirects=True,
    )
    assert b"Invalid location coordinates." in response.data
    assert b"Saved at:" not in response.data


def test_parking_rejects_out_of_range_coordinates(client, login):
    login()
    response = client.post(
        "/parking/",
        data={
            "location": "Garage H",
            "level": "",
            "row": "",
            "notes": "",
            "latitude": "200",
            "longitude": "-122.4194",
        },
        follow_redirects=True,
    )
    assert b"Invalid location coordinates." in response.data
    assert b"Saved at:" not in response.data
