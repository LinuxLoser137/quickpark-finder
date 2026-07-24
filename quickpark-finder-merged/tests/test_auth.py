def test_register_and_login_flow(client):
    response = client.post(
        "/auth/register/",
        data={"username": "alice", "password": "secret123"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Log In" in response.data

    response = client.post(
        "/auth/login/",
        data={"username": "alice", "password": "secret123"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Main Menu" in response.data


def test_register_requires_username_and_password(client):
    response = client.post("/auth/register/", data={"username": "", "password": ""})
    assert b"Username is required." in response.data

def test_register_requires_password_when_username_present(client):
    response = client.post("/auth/register/", data={"username": "erin", "password": ""})
    assert b"Password is required." in response.data

def test_register_rejects_overlong_username(client):
    response = client.post(
        "/auth/register/",
        data={"username": "x" * 81, "password": "secret123"},
    )
    assert b"Username is too long." in response.data

def test_parking_rejects_overlong_level(client, login):
    login()
    response = client.post(
        "/parking/",
        data={"location": "Garage A", "level": "x"*51, "row":"", "notes":""},
        follow_redirects=True,
    )
    assert b"Level/Row is too long." in response.data

def test_parking_rejects_overlong_landmark(client, login):
    login()
    response = client.post(
        "/parking/",
        data={"location": "Garage A", "level": "x", "row":"","landmark": "x"*201, "notes":""},
        follow_redirects=True,
    )
    assert b"Landmark is too long." in response.data

def test_parking_rejects_overlong_notes(client, login):
    login()
    response = client.post(
        "/parking/",
        data={"location": "Garage A", "level": "", "row": "", "notes": "x" * 1001},
        follow_redirects=True,
    )
    assert b"Notes is too long." in response.data

def test_register_rejects_short_password(client):
    response = client.post("/auth/register/", data={"username": "bob", "password": "123"})
    assert b"Password must be at least 8 characters." in response.data

def test_register_rejects_duplicate_username(client, register):
    register("carol", "secret123")
    response = client.post(
        "/auth/register/",
        data={"username": "carol", "password": "different1"},
        follow_redirects=True,
    )
    assert b"already registered" in response.data


def test_login_rejects_unknown_username(client):
    response = client.post(
        "/auth/login/", data={"username": "ghost", "password": "whatever1"}
    )
    assert b"Incorrect username." in response.data


def test_login_rejects_wrong_password(client, register):
    register("dave", "correct-horse")
    response = client.post(
        "/auth/login/", data={"username": "dave", "password": "wrong-horse"}
    )
    assert b"Incorrect password." in response.data

def test_logout_clears_session(client, login):
    login()
    client.get("/auth/logout/")
    
    response = client.get("/parking/", follow_redirects=True)
    assert b"Log In" in response.data