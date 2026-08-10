import functools
import sqlite3

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from .db import get_db


bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
)


@bp.route("/register/", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form.get(
            "username",
            "",
        ).strip()

        password = request.form.get(
            "password",
            "",
        )

        db = get_db()
        error = None

        if not username:
            error = "Username is required."

        elif not password:
            error = "Password is required."

        elif len(username) > 80:
            error = "Username is too long."

        elif len(password) < 8:
            error = (
                "Password must be at least "
                "8 characters."
            )

        if error is None:
            try:
                db.execute(
                    """
                    INSERT INTO user
                        (username, password)
                    VALUES (?, ?)
                    """,
                    (
                        username,
                        generate_password_hash(
                            password
                        ),
                    ),
                )

                db.commit()

            except sqlite3.IntegrityError:
                error = (
                    f"User {username} is "
                    "already registered."
                )

            else:
                return redirect(
                    url_for("auth.login")
                )

        if error is not None:
            flash(error)

    return render_template(
        "auth/register.html"
    )


@bp.route("/login/", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get(
            "username",
            "",
        ).strip()

        password = request.form.get(
            "password",
            "",
        )

        db = get_db()
        error = None

        user = db.execute(
            """
            SELECT *
            FROM user
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

        if user is None:
            error = "Incorrect username."

        elif not check_password_hash(
            user["password"],
            password,
        ):
            error = "Incorrect password."

        if error is None and user is not None:
            session.clear()

            session["user_id"] = user["id"]

            # Marks the login session as permanent
            # so Flask's 15-minute session lifetime
            # setting can be enforced.
            session.permanent = True

            return redirect(
                url_for("index")
            )

        if error is not None:
            flash(error)

    return render_template(
        "auth/login.html"
    )


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None

    else:
        g.user = get_db().execute(
            """
            SELECT *
            FROM user
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()


@bp.route("/logout/")
def logout():
    session.clear()

    return redirect(
        url_for("index")
    )


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(
                url_for("auth.login")
            )

        return view(**kwargs)

    return wrapped_view
