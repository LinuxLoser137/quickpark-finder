def test_quickpark_requires_login(client):
    response = client.get("/quickpark/", follow_redirects=True)
    assert b"Log In" in response.data


def test_quickpark_only_shows_own_saved_locations(client, login, register):
    login("alice", "secret123")
    client.post("/parking/", data={"location": "Alice Garage", "level": "", "row": "", "notes": ""})
    client.get("/auth/logout/")

    register("bob", "secret123")
    client.post("/auth/login/", data={"username": "bob", "password": "secret123"}, follow_redirects=True)
    client.post("/parking/", data={"location": "Bob Garage", "level": "", "row": "", "notes": ""})

    response = client.get("/quickpark/")
    assert b"Bob Garage" in response.data
    assert b"Alice Garage" not in response.data


def test_quickpark_limits_to_five_most_recent(client, login):
    login()
    for i in range(7):
        client.post("/parking/", data={"location": f"Spot {i}", "level": "", "row": "", "notes": ""})

    response = client.get("/quickpark/")
    assert response.data.count(b"Spot ") == 5
    assert b"Spot 6" in response.data
    assert b"Spot 0" not in response.data
    assert  response.data.index(b"Spot 6") < response.data.index(b"Spot 2")


def test_quickpark_list_shows_directions_link_when_coordinates_saved(client, login):
    login()
    client.post(
        "/parking/",
        data={
            "location": "Garage With Coords",
            "level": "",
            "row": "",
            "notes": "",
            "latitude": "37.7749",
            "longitude": "-122.4194",
        },
    )
    client.post(
        "/parking/",
        data={"location": "Garage Without Coords", "level": "", "row": "", "notes": ""},
    )

    response = client.get("/quickpark/")
    assert response.data.count(b"Get Directions") == 1
    assert b"37.7749" not in response.data
