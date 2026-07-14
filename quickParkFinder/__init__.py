import os
from flask import Flask, redirect, render_template, request, url_for


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
        return 'Hello, World!'

    @app.route('/parking/', methods=('GET', 'POST'))
    def parking():
        error = None
        parking_record = None

        if request.method == 'POST':
            location = request.form.get('location', '').strip()
            level = request.form.get('level', '').strip()
            row = request.form.get('row', '').strip()
            notes = request.form.get('notes', '').strip()

            if not location:
                error = 'Location is required.'
            else:
                parking_record = {
                    'location': location,
                    'level': level,
                    'row': row,
                    'notes': notes,
                }
                app.config.setdefault('parking_records', []).append(parking_record)

        return render_template('parking.html', error=error, parking_record=parking_record)

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    return app