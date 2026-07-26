import smtplib
from email.message import EmailMessage

from flask import current_app

from .settings_store import get_setting


def _format_alert_body(hostname, tests):
    failed = [t for t in tests if not t.get("pass", False)]
    lines = [f"lorikeet run on {hostname} has {len(failed)} failing check(s):", ""]
    for t in failed:
        lines.append(f"- {t.get('name')}: {t.get('error') or t.get('output') or ''}")
    return "\n".join(lines)


def send_email(subject, body):
    host = get_setting("email_smtp_host")
    port = int(get_setting("email_smtp_port", "587") or "587")
    user = get_setting("email_smtp_user")
    password = get_setting("email_smtp_pass")
    from_addr = get_setting("email_from")
    to_addr = get_setting("email_to")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(body)

    with smtplib.SMTP(host, port, timeout=10) as smtp:
        smtp.starttls()
        if user:
            smtp.login(user, password)
        smtp.send_message(msg)


def send_sms(body):
    from twilio.rest import Client

    client = Client(get_setting("twilio_account_sid"), get_setting("twilio_auth_token"))
    client.messages.create(
        body=body[:1600],
        from_=get_setting("twilio_from_number"),
        to=get_setting("twilio_to_number"),
    )


def dispatch_alerts(hostname, tests):
    subject = f"lorikeet failure on {hostname}"
    body = _format_alert_body(hostname, tests)

    if get_setting("email_enabled", "0") == "1":
        try:
            send_email(subject, body)
        except Exception:
            current_app.logger.exception("Failed to send email alert")

    if get_setting("sms_enabled", "0") == "1":
        try:
            send_sms(body)
        except Exception:
            current_app.logger.exception("Failed to send SMS alert")
