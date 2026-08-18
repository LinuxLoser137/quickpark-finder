import os
from datetime import timedelta

from flask import (
    Flask,
    abort,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from .auth import login_required
from .crypto import decrypt_coordinate, encrypt_coordinate
from .db import get_db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "quickParkFinder.sqlite"),
        MAX_CONTENT_LENGTH=64 * 1024,
        SESSION_COOKIE_SAMESITE="Lax",

        # Automatically expire a permanent login session after 15 minutes.
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=15),

        # Refresh the session expiration time whenever the user makes a request.
        SESSION_REFRESH_EACH_REQUEST=True,
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    @app.route("/")
    def index():
        return redirect(url_for("hello"))

    @app.route("/hello/")
    def hello():
        return render_template("hello.html")

    @app.route("/parking/", methods=("GET", "POST"))
    @login_required
    def parking():
        error = None
        parking_record = None
        db = get_db()

        if request.method == "POST":
            location = request.form.get("location", "").strip()
            level = request.form.get("level", "").strip()
            row = request.form.get("row", "").strip()
            landmark = request.form.get("landmark", "").strip()
            notes = request.form.get("notes", "").strip()
            latitude_raw = request.form.get("latitude", "").strip()
            longitude_raw = request.form.get("longitude", "").strip()

            latitude = None
            longitude = None
            coordinates_valid = True

            if latitude_raw or longitude_raw:
                try:
                    latitude = float(latitude_raw)
                    longitude = float(longitude_raw)

                    if not (-90 <= latitude <= 90):
                        coordinates_valid = False

                    if not (-180 <= longitude <= 180):
                        coordinates_valid = False

                except ValueError:
                    coordinates_valid = False

            if not location:
                error = "Location is required."

            elif len(location) > 200:
                error = "Location is too long."

            elif len(level) > 50 or len(row) > 50:
                error = "Level/Row is too long."

            elif len(landmark) > 200:
                error = "Landmark is too long."

            elif len(notes) > 1000:
                error = "Notes is too long."

            elif not coordinates_valid:
                error = "Invalid location coordinates."

            else:
                cursor = db.execute(
                    """
                    INSERT INTO quickpark
                        (
                            user_id,
                            location,
                            level,
                            row,
                            landmark,
                            notes,
                            latitude,
                            longitude
                        )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        g.user["id"],
                        location,
                        level,
                        row,
                        landmark,
                        notes,
                        encrypt_coordinate(latitude)
                        if latitude is not None
                        else None,
                        encrypt_coordinate(longitude)
                        if longitude is not None
                        else None,
                    ),
                )

                db.commit()

                saved_row = db.execute(
                    "SELECT * FROM quickpark WHERE id = ?",
                    (cursor.lastrowid,),
                ).fetchone()

                parking_record = dict(saved_row)

        return render_template(
            "parking.html",
            error=error,
            parking_record=parking_record,
        )

    @app.route("/quickpark/")
    @login_required
    def quickpark_list():
        db = get_db()

        quickparks = db.execute(
            """
            SELECT *
            FROM quickpark
            WHERE user_id = ?
            ORDER BY created DESC, id DESC
            LIMIT 5
            """,
            (g.user["id"],),
        ).fetchall()

        return render_template(
            "quickparks.html",
            quickparks=quickparks,
        )

    @app.route("/quickpark/<int:quickpark_id>/clear", methods=("POST",))
    @login_required
    def clear_quickpark(quickpark_id):
        db = get_db()

        quickpark = db.execute(
            """
            SELECT id
            FROM quickpark
            WHERE id = ? AND user_id = ?
            """,
            (quickpark_id, g.user["id"]),
        ).fetchone()

        if quickpark is None:
            abort(404)

        db.execute(
            """
            DELETE FROM quickpark
            WHERE id = ? AND user_id = ?
            """,
            (quickpark_id, g.user["id"]),
        )

        db.commit()

        return redirect(url_for("quickpark_list"))

    @app.route("/quickpark/<int:quickpark_id>/directions")
    @login_required
    def get_directions(quickpark_id):
        db = get_db()

        row = db.execute(
            """
            SELECT latitude, longitude
            FROM quickpark
            WHERE id = ? AND user_id = ?
            """,
            (quickpark_id, g.user["id"]),
        ).fetchone()

        if row is None or not row["latitude"] or not row["longitude"]:
            abort(404)

        lat = decrypt_coordinate(row["latitude"])
        lng = decrypt_coordinate(row["longitude"])

        return redirect(
            f"https://www.google.com/maps/dir/"
            f"?api=1&destination={lat},{lng}"
        )

    from . import db

    db.init_app(app)

    from . import auth

    app.register_blueprint(auth.bp)

    return app
