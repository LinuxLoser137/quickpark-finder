# QuickPark Finder

This merged Flask application combines the working parking form and styling with the packaged Flask structure, authentication, SQLite storage, and automated tests.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[test]"
```

## Initialize the database

```powershell
flask --app quickParkFinder init-db
```

## Run the app

```powershell
flask --app quickParkFinder run --debug
```

Open `http://127.0.0.1:5000`.

## Run tests

```powershell
pytest
```

## Important security note

Passwords are hashed using Werkzeug. Parking-location fields are stored in SQLite but are **not encrypted at rest** in this version.
