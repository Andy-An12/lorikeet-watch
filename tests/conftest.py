import pytest

from lorikeet_watch import create_app
from lorikeet_watch.auth import set_admin_credentials
from lorikeet_watch.db import init_db
from lorikeet_watch.settings_store import set_setting


@pytest.fixture
def app(tmp_path):
    db_path = tmp_path / "test.sqlite"
    app = create_app({"TESTING": True, "DATABASE": str(db_path), "SECRET_KEY": "test"})
    with app.app_context():
        init_db()
        set_admin_credentials("admin", "password123")
        set_setting("ingest_token", "test-token")
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def logged_in_client(client):
    client.post(
        "/api/login",
        json={"username": "admin", "password": "password123"},
    )
    return client
