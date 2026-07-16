import os
from flask import Flask, redirect, render_template, request, url_for, g
from .db import get_db
from .auth import login_required


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'quickParkFinder.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    @app.route('/')
    def index():
        return redirect(url_for('hello'))

    @app.route('/hello/')
    def hello():
        return render_template('hello.html')

    @app.route('/parking/', methods=('GET', 'POST'))
    @login_required
    def parking():
        error = None
        parking_record = None
        db = get_db()

        if request.method == 'POST':
            location = request.form.get('location', '').strip()
            level = request.form.get('level', '').strip()
            row = request.form.get('row', '').strip()
            notes = request.form.get('notes', '').strip()

            if not location:
                error = 'Location is required.'
            else:
                db.execute(
                    'INSERT INTO quickpark (user_id, location, level, row, notes)'
                    ' VALUES (?, ?, ?, ?, ?)',
                    (g.user['id'], location, level, row, notes)
                )
                db.commit()
                parking_record = {'location': location, 'level': level, 'row': row, 'notes': notes}

        return render_template('parking.html', error=error, parking_record=parking_record)

    
    @app.route('/quickpark/')
    @login_required
    def quickpark_list():
        db = get_db()
        quickparks = db.execute(
            'SELECT * FROM quickpark WHERE user_id = ? ORDER BY created DESC LIMIT 5',
            (g.user['id'],)
        ).fetchall()
        return render_template('quickpark.html', quickparks=quickparks)
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    return app