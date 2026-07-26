import json
from unittest.mock import patch

from lorikeet_watch import ingest
from lorikeet_watch.db import get_db

VALID_PAYLOAD = {
    "hostname": "server1.example.com",
    "has_errors": True,
    "tests": [
        {
            "name": "disk_free",
            "pass": False,
            "output": "",
            "error": "only 500MB free",
            "duration": 1.23,
        },
        {
            "name": "mem_available",
            "pass": True,
            "output": "ok",
            "error": None,
            "duration": 0.45,
        },
    ],
}


def test_rejects_missing_token(client):
    response = client.post("/internal/results", json=VALID_PAYLOAD)
    assert response.status_code == 401


def test_rejects_wrong_token(client):
    response = client.post(
        "/internal/results?token=wrong", json=VALID_PAYLOAD
    )
    assert response.status_code == 401


def test_rejects_malformed_payload(client):
    response = client.post(
        "/internal/results?token=test-token", json={"nope": True}
    )
    assert response.status_code == 400


def test_accepts_valid_payload_and_persists_run_and_steps(client, app):
    response = client.post(
        "/internal/results?token=test-token", json=VALID_PAYLOAD
    )
    assert response.status_code == 200

    with app.app_context():
        db = get_db()
        run = db.execute("SELECT * FROM runs WHERE hostname = ?", ("server1.example.com",)).fetchone()
        assert run is not None
        assert run["has_errors"] == 1

        steps = db.execute("SELECT * FROM steps WHERE run_id = ?", (run["id"],)).fetchall()
        assert len(steps) == 2
        names = {s["name"] for s in steps}
        assert names == {"disk_free", "mem_available"}


def test_dispatches_alerts_on_failing_run(client):
    with patch.object(ingest, "dispatch_alerts") as mock_dispatch:
        client.post("/internal/results?token=test-token", json=VALID_PAYLOAD)
        mock_dispatch.assert_called_once_with(
            "server1.example.com", VALID_PAYLOAD["tests"]
        )


def test_does_not_dispatch_alerts_on_passing_run(client):
    passing_payload = {
        "hostname": "server2.example.com",
        "has_errors": False,
        "tests": [{"name": "mem_available", "pass": True, "output": "ok", "error": None, "duration": 0.1}],
    }
    with patch.object(ingest, "dispatch_alerts") as mock_dispatch:
        client.post("/internal/results?token=test-token", json=passing_payload)
        mock_dispatch.assert_not_called()
