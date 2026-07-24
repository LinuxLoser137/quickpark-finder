import os
from flask import Flask, redirect, render_template, request, url_for, g
from .db import get_db
from .auth import login_required


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "quickParkFinder.sqlite"),
        MAX_CONTENT_LENGTH=64 * 1024,
        SESSION_COOKIE_SAMESITE="Lax",
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
            else:
                cursor = db.execute(
                    """
                    INSERT INTO quickpark
                        (user_id, location, level, row, landmark, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (g.user["id"], location, level, row, landmark, notes),
                )
                db.commit()
                saved_row = db.execute(
                    "SELECT * FROM quickpark WHERE id = ?", (cursor.lastrowid,)
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
        return render_template("quickparks.html", quickparks=quickparks)

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    return app
