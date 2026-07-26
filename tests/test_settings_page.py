from lorikeet_watch.settings_store import get_setting, set_setting


def test_settings_page_requires_login(client):
    response = client.get("/api/settings")
    assert response.status_code == 401


def test_post_settings_saves_email_and_sms_config(app, logged_in_client):
    response = logged_in_client.post(
        "/api/settings",
        json={
            "email_enabled": True,
            "email_smtp_host": "smtp.example.com",
            "email_smtp_port": "587",
            "email_smtp_user": "user",
            "email_smtp_pass": "pass",
            "email_from": "alerts@example.com",
            "email_to": "admin@example.com",
            "sms_enabled": True,
            "twilio_account_sid": "SID123",
            "twilio_auth_token": "TOKEN123",
            "twilio_from_number": "+15550001111",
            "twilio_to_number": "+15550002222",
        },
    )
    assert response.status_code == 200
    assert response.get_json() == {"ok": True}

    with app.app_context():
        assert get_setting("email_enabled") == "1"
        assert get_setting("email_smtp_host") == "smtp.example.com"
        assert get_setting("sms_enabled") == "1"
        assert get_setting("twilio_account_sid") == "SID123"


def test_post_settings_disables_channel_when_flag_omitted(app, logged_in_client):
    logged_in_client.post(
        "/api/settings",
        json={
            "email_smtp_host": "smtp.example.com",
            "email_smtp_port": "587",
            "email_smtp_user": "",
            "email_smtp_pass": "",
            "email_from": "",
            "email_to": "",
            "twilio_account_sid": "",
            "twilio_auth_token": "",
            "twilio_from_number": "",
            "twilio_to_number": "",
        },
    )
    with app.app_context():
        assert get_setting("email_enabled") == "0"
        assert get_setting("sms_enabled") == "0"


def test_post_settings_blank_secret_keeps_existing_value(app, logged_in_client):
    with app.app_context():
        set_setting("email_smtp_pass", "old-smtp-pass")
        set_setting("twilio_auth_token", "old-twilio-token")

    logged_in_client.post(
        "/api/settings",
        json={
            "email_smtp_host": "smtp.example.com",
            "email_smtp_port": "587",
            "email_smtp_user": "user",
            "email_smtp_pass": "",
            "email_from": "alerts@example.com",
            "email_to": "admin@example.com",
            "twilio_account_sid": "SID123",
            "twilio_auth_token": "",
            "twilio_from_number": "+15550001111",
            "twilio_to_number": "+15550002222",
        },
    )

    with app.app_context():
        assert get_setting("email_smtp_pass") == "old-smtp-pass"
        assert get_setting("twilio_auth_token") == "old-twilio-token"


def test_settings_response_does_not_leak_secrets(app, logged_in_client):
    with app.app_context():
        set_setting("email_smtp_pass", "supersecretpw123")

    response = logged_in_client.get("/api/settings")
    data = response.get_json()

    assert "email_smtp_pass" not in data
    assert "twilio_auth_token" not in data
    assert "admin_password_hash" not in data


def test_regenerate_token_changes_ingest_token(app, logged_in_client):
    with app.app_context():
        original = get_setting("ingest_token")

    response = logged_in_client.post("/api/settings/regenerate-token")
    assert response.status_code == 200

    with app.app_context():
        assert get_setting("ingest_token") != original
        assert get_setting("ingest_token") != ""
