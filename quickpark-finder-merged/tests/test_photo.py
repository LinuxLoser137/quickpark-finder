import io

from quickParkFinder.db import get_db

FAKE_JPEG_BYTES = b"fake-jpeg-bytes-not-a-real-image"
REAL_JPEG_BYTES = b"\xff\xd8\xff" + b"fake-body-behind-a-real-jpeg-header"


def _photo_file(data=REAL_JPEG_BYTES, filename="spot.jpg", content_type="image/jpeg"):
    return (io.BytesIO(data), filename, content_type)


def test_parking_photo_is_optional(client, login):
    login()
    response = client.post(
        "/parking/",
        data={"location": "Garage I", "level": "", "row": "", "notes": ""},
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Saved at:" in response.data
    assert b'class="quickpark-photo"' not in response.data


def test_parking_with_photo_shows_thumbnail(client, login):
    login()
    response = client.post(
        "/parking/",
        data={
            "location": "Garage J",
            "level": "",
            "row": "",
            "notes": "",
            "photo": _photo_file(),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Saved at:" in response.data
    assert b'class="quickpark-photo"' in response.data
    assert b"/photo" in response.data


def test_parking_rejects_disallowed_photo_type(client, login):
    login()
    response = client.post(
        "/parking/",
        data={
            "location": "Garage K",
            "level": "",
            "row": "",
            "notes": "",
            "photo": _photo_file(
                data=b"not an image",
                filename="notes.txt",
                content_type="text/plain",
            ),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert b"Photo must be a JPEG, PNG, GIF, or WEBP image under 5MB." in response.data
    assert b"Saved at:" not in response.data


def test_parking_rejects_mislabeled_non_image_bytes(client, login):
    login()
    response = client.post(
        "/parking/",
        data={
            "location": "Garage Q",
            "level": "",
            "row": "",
            "notes": "",
            "photo": _photo_file(data=FAKE_JPEG_BYTES),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert b"Photo must be a JPEG, PNG, GIF, or WEBP image under 5MB." in response.data
    assert b"Saved at:" not in response.data


def test_parking_rejects_oversized_photo(client, login):
    login()
    oversized = b"\xff\xd8\xff" + b"x" * (5 * 1024 * 1024 + 1)
    response = client.post(
        "/parking/",
        data={
            "location": "Garage L",
            "level": "",
            "row": "",
            "notes": "",
            "photo": _photo_file(data=oversized),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )

    assert b"Photo must be a JPEG, PNG, GIF, or WEBP image under 5MB." in response.data
    assert b"Saved at:" not in response.data


def test_photo_is_encrypted_at_rest(client, login, app):
    login()
    client.post(
        "/parking/",
        data={
            "location": "Garage M",
            "level": "",
            "row": "",
            "notes": "",
            "photo": _photo_file(),
        },
        content_type="multipart/form-data",
    )

    with app.app_context():
        row = get_db().execute(
            "SELECT photo, photo_mimetype FROM quickpark WHERE location = ?",
            ("Garage M",),
        ).fetchone()

    assert row["photo"] is not None
    assert REAL_JPEG_BYTES not in row["photo"]
    assert row["photo_mimetype"] == "image/jpeg"


def test_photo_route_returns_decrypted_photo_to_owner(client, login):
    login()
    client.post(
        "/parking/",
        data={
            "location": "Garage N",
            "level": "",
            "row": "",
            "notes": "",
            "photo": _photo_file(),
        },
        content_type="multipart/form-data",
    )

    response = client.get("/quickpark/1/photo")
    assert response.status_code == 200
    assert response.data == REAL_JPEG_BYTES
    assert response.mimetype == "image/jpeg"


def test_photo_route_rejects_other_users_quickpark(client, login, register):
    login("alice", "secret123")
    client.post(
        "/parking/",
        data={
            "location": "Alice Garage",
            "level": "",
            "row": "",
            "notes": "",
            "photo": _photo_file(),
        },
        content_type="multipart/form-data",
    )
    client.get("/auth/logout/")

    register("bob", "secret123")
    client.post("/auth/login/", data={"username": "bob", "password": "secret123"}, follow_redirects=True)

    response = client.get("/quickpark/1/photo")
    assert response.status_code == 404


def test_photo_route_404s_when_no_photo_saved(client, login):
    login()
    client.post(
        "/parking/",
        data={"location": "Garage O", "level": "", "row": "", "notes": ""},
        content_type="multipart/form-data",
    )

    response = client.get("/quickpark/1/photo")
    assert response.status_code == 404


def test_quickpark_list_shows_photo_thumbnail(client, login):
    login()
    client.post(
        "/parking/",
        data={
            "location": "Garage With Photo",
            "level": "",
            "row": "",
            "notes": "",
            "photo": _photo_file(),
        },
        content_type="multipart/form-data",
    )
    client.post(
        "/parking/",
        data={"location": "Garage Without Photo", "level": "", "row": "", "notes": ""},
        content_type="multipart/form-data",
    )

    response = client.get("/quickpark/")
    assert response.data.count(b'class="quickpark-photo"') == 1
