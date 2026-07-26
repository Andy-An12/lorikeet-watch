import hmac

from flask import Blueprint, jsonify, request

from .alerts import dispatch_alerts
from .db import get_db
from .settings_store import get_setting

bp = Blueprint("ingest", __name__)


@bp.route("/internal/results", methods=["POST"])
def receive_results():
    token = request.args.get("token", "")
    expected = get_setting("ingest_token", "")
    if not expected or not hmac.compare_digest(token, expected):
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json(silent=True)
    if not payload or "hostname" not in payload or "tests" not in payload:
        return jsonify({"error": "invalid payload"}), 400

    db = get_db()
    cursor = db.execute(
        "INSERT INTO runs (hostname, has_errors) VALUES (?, ?)",
        (payload["hostname"], bool(payload.get("has_errors", False))),
    )
    run_id = cursor.lastrowid

    for test in payload["tests"]:
        db.execute(
            "INSERT INTO steps (run_id, name, pass, output, error, duration) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                run_id,
                test.get("name", ""),
                bool(test.get("pass", False)),
                test.get("output"),
                test.get("error"),
                test.get("duration"),
            ),
        )
    db.commit()

    if payload.get("has_errors"):
        dispatch_alerts(payload["hostname"], payload["tests"])

    return jsonify({"status": "ok"}), 200
