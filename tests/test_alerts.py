from unittest.mock import patch

from lorikeet_watch import alerts
from lorikeet_watch.settings_store import set_setting

FAILING_TESTS = [
    {"name": "disk_free", "pass": False, "error": "only 500MB free", "output": ""},
    {"name": "mem_available", "pass": True, "error": None, "output": "ok"},
]


def test_dispatch_alerts_calls_email_when_enabled(app):
    with app.app_context():
        set_setting("email_enabled", "1")
        set_setting("sms_enabled", "0")
        with patch.object(alerts, "send_email") as mock_email, patch.object(
            alerts, "send_sms"
        ) as mock_sms:
            alerts.dispatch_alerts("server1", FAILING_TESTS)
            assert mock_email.call_count == 1
            assert mock_sms.call_count == 0


def test_dispatch_alerts_calls_sms_when_enabled(app):
    with app.app_context():
        set_setting("email_enabled", "0")
        set_setting("sms_enabled", "1")
        with patch.object(alerts, "send_email") as mock_email, patch.object(
            alerts, "send_sms"
        ) as mock_sms:
            alerts.dispatch_alerts("server1", FAILING_TESTS)
            assert mock_email.call_count == 0
            assert mock_sms.call_count == 1


def test_dispatch_alerts_sends_nothing_when_both_disabled(app):
    with app.app_context():
        set_setting("email_enabled", "0")
        set_setting("sms_enabled", "0")
        with patch.object(alerts, "send_email") as mock_email, patch.object(
            alerts, "send_sms"
        ) as mock_sms:
            alerts.dispatch_alerts("server1", FAILING_TESTS)
            assert mock_email.call_count == 0
            assert mock_sms.call_count == 0


def test_dispatch_alerts_swallows_send_errors(app):
    with app.app_context():
        set_setting("email_enabled", "1")
        set_setting("sms_enabled", "1")
        with patch.object(
            alerts, "send_email", side_effect=RuntimeError("smtp down")
        ), patch.object(alerts, "send_sms", side_effect=RuntimeError("twilio down")):
            # Must not raise.
            alerts.dispatch_alerts("server1", FAILING_TESTS)


def test_send_email_uses_configured_smtp_settings(app):
    with app.app_context():
        set_setting("email_smtp_host", "smtp.example.com")
        set_setting("email_smtp_port", "587")
        set_setting("email_smtp_user", "user")
        set_setting("email_smtp_pass", "pass")
        set_setting("email_from", "alerts@example.com")
        set_setting("email_to", "admin@example.com")

        with patch("lorikeet_watch.alerts.smtplib.SMTP") as mock_smtp_cls:
            mock_smtp = mock_smtp_cls.return_value.__enter__.return_value
            alerts.send_email("subject", "body")

            mock_smtp_cls.assert_called_once_with("smtp.example.com", 587, timeout=10)
            mock_smtp.starttls.assert_called_once()
            mock_smtp.login.assert_called_once_with("user", "pass")
            mock_smtp.send_message.assert_called_once()
