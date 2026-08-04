import base64
import hashlib

from cryptography.fernet import Fernet
from flask import current_app


def _fernet():
    # ponytail: key is derived from SECRET_KEY, so it's only as strong as
    # that config value. Fine for "not sitting in the DB as plaintext";
    # rotate/replace once SECRET_KEY moves off the hardcoded "dev" default.
    key = hashlib.sha256(current_app.config["SECRET_KEY"].encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt_coordinate(value):
    return _fernet().encrypt(str(value).encode()).decode()


def decrypt_coordinate(token):
    return float(_fernet().decrypt(token.encode()).decode())
