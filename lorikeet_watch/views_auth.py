from flask import Blueprint, jsonify, request, session

from .auth import verify_admin_credentials

bp = Blueprint("views_auth", __name__)


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")
    if verify_admin_credentials(username, password):
        session.clear()
        session["logged_in"] = True
        session["username"] = username
        return jsonify({"ok": True})
    return jsonify({"error": "invalid credentials"}), 401


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


@bp.route("/session")
def get_session():
    if not session.get("logged_in"):
        return jsonify({"logged_in": False}), 401
    return jsonify({"logged_in": True, "username": session.get("username")})
