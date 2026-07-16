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
