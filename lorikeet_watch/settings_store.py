from .db import get_db

DEFAULTS = {
    "admin_username": "",
    "admin_password_hash": "",
    "ingest_token": "",
    "email_enabled": "0",
    "email_smtp_host": "",
    "email_smtp_port": "587",
    "email_smtp_user": "",
    "email_smtp_pass": "",
    "email_from": "",
    "email_to": "",
    "sms_enabled": "0",
    "twilio_account_sid": "",
    "twilio_auth_token": "",
    "twilio_from_number": "",
    "twilio_to_number": "",
}


def get_setting(key, default=""):
    db = get_db()
    row = db.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    if row is None:
        return DEFAULTS.get(key, default)
    return row["value"]


def get_all_settings():
    return {key: get_setting(key) for key in DEFAULTS}


def set_setting(key, value):
    db = get_db()
    db.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
    db.commit()


def set_settings(pairs):
    for key, value in pairs.items():
        set_setting(key, value)
