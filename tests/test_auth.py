from flask import Flask

from lorikeet_watch.auth import (
    login_required,
    set_admin_credentials,
    verify_admin_credentials,
)


def test_set_and_verify_admin_credentials(app):
    with app.app_context():
        set_admin_credentials("admin", "s3cret")
        assert verify_admin_credentials("admin", "s3cret") is True
        assert verify_admin_credentials("admin", "wrong") is False
        assert verify_admin_credentials("nobody", "s3cret") is False


def test_login_required_returns_401_json_when_not_logged_in(app):
    protected = Flask(__name__)
    protected.secret_key = "test"

    @protected.route("/protected")
    @login_required
    def protected_view():
        return "secret"

    client = protected.test_client()
    response = client.get("/protected")
    assert response.status_code == 401
    assert response.get_json() == {"error": "unauthorized"}


def test_login_accepts_correct_credentials(app, client):
    with app.app_context():
        set_admin_credentials("admin", "s3cret")
    response = client.post(
        "/api/login", json={"username": "admin", "password": "s3cret"}
    )
    assert response.status_code == 200
    assert response.get_json() == {"ok": True}


def test_login_rejects_wrong_password(app, client):
    with app.app_context():
        set_admin_credentials("admin", "s3cret")
    response = client.post(
        "/api/login", json={"username": "admin", "password": "wrong"}
    )
    assert response.status_code == 401
    assert response.get_json() == {"error": "invalid credentials"}


def test_session_reports_logged_in_state(logged_in_client):
    response = logged_in_client.get("/api/session")
    assert response.status_code == 200
    assert response.get_json() == {"logged_in": True, "username": "admin"}


def test_session_reports_logged_out_state(client):
    response = client.get("/api/session")
    assert response.status_code == 401
    assert response.get_json() == {"logged_in": False}


def test_logout_clears_session(logged_in_client):
    response = logged_in_client.post("/api/logout")
    assert response.status_code == 200
    session_response = logged_in_client.get("/api/session")
    assert session_response.status_code == 401
