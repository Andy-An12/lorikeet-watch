from functools import wraps

from flask import jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash

from .settings_store import get_setting, set_setting


def set_admin_credentials(username, password):
    set_setting("admin_username", username)
    set_setting(
        "admin_password_hash", generate_password_hash(password, method="pbkdf2:sha256")
    )


def verify_admin_credentials(username, password):
    stored_username = get_setting("admin_username", "")
    stored_hash = get_setting("admin_password_hash", "")
    if not stored_hash or username != stored_username:
        return False
    return check_password_hash(stored_hash, password)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            return jsonify({"error": "unauthorized"}), 401
        return view(*args, **kwargs)

    return wrapped
