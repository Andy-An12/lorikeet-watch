from lorikeet_watch.settings_store import get_setting, set_setting, get_all_settings


def test_get_setting_returns_default_when_unset(app):
    with app.app_context():
        assert get_setting("email_enabled") == "0"


def test_set_then_get_roundtrips(app):
    with app.app_context():
        set_setting("email_enabled", "1")
        assert get_setting("email_enabled") == "1"


def test_set_setting_overwrites_existing_value(app):
    with app.app_context():
        set_setting("email_from", "a@example.com")
        set_setting("email_from", "b@example.com")
        assert get_setting("email_from") == "b@example.com"


def test_get_all_settings_includes_defaults(app):
    with app.app_context():
        all_settings = get_all_settings()
        assert all_settings["sms_enabled"] == "0"
        assert "twilio_account_sid" in all_settings
