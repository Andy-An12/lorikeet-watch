import secrets

from flask import Blueprint, jsonify, request

from .auth import login_required, set_admin_credentials
from .settings_store import get_all_settings, get_setting, set_setting, set_settings

bp = Blueprint("views_settings", __name__)

TEXT_FIELDS = [
    "email_smtp_host",
    "email_smtp_port",
    "email_smtp_user",
    "email_smtp_pass",
    "email_from",
    "email_to",
    "twilio_account_sid",
    "twilio_auth_token",
    "twilio_from_number",
    "twilio_to_number",
]

SECRET_FIELDS = ("email_smtp_pass", "twilio_auth_token")
RESPONSE_EXCLUDE_FIELDS = ("email_smtp_pass", "twilio_auth_token", "admin_password_hash")


@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings_page():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        values = {field: str(data.get(field, "")) for field in TEXT_FIELDS}
        for secret_field in SECRET_FIELDS:
            if not values[secret_field]:
                values[secret_field] = get_setting(secret_field, "")
        values["email_enabled"] = "1" if data.get("email_enabled") else "0"
        values["sms_enabled"] = "1" if data.get("sms_enabled") else "0"
        set_settings(values)

        new_password = str(data.get("new_password", "")).strip()
        if new_password:
            username = str(data.get("username", "admin")).strip() or "admin"
            set_admin_credentials(username, new_password)

        return jsonify({"ok": True})

    settings = get_all_settings()
    for field in RESPONSE_EXCLUDE_FIELDS:
        settings.pop(field, None)
    return jsonify(settings)


@bp.route("/settings/regenerate-token", methods=["POST"])
@login_required
def regenerate_token():
    set_setting("ingest_token", secrets.token_urlsafe(32))
    return jsonify({"ok": True})
