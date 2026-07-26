from lorikeet_watch.db import get_db


def seed_run(app, hostname, has_errors, step_name, step_pass):
    with app.app_context():
        db = get_db()
        cursor = db.execute(
            "INSERT INTO runs (hostname, has_errors) VALUES (?, ?)",
            (hostname, has_errors),
        )
        run_id = cursor.lastrowid
        db.execute(
            "INSERT INTO steps (run_id, name, pass, output, error, duration) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (run_id, step_name, step_pass, "out", None, 1.0),
        )
        db.commit()
        return run_id


def test_dashboard_requires_login(client):
    response = client.get("/api/dashboard")
    assert response.status_code == 401


def test_dashboard_shows_latest_run_per_hostname(app, logged_in_client):
    seed_run(app, "server1", False, "disk_free", True)
    seed_run(app, "server1", True, "disk_free", False)  # latest for server1
    seed_run(app, "server2", False, "mem_available", True)

    response = logged_in_client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.get_json()
    runs_by_host = {run["hostname"]: run for run in data["runs"]}
    assert runs_by_host["server1"]["has_errors"] is True
    assert runs_by_host["server2"]["has_errors"] is False


def test_host_history_requires_login(client):
    response = client.get("/api/hosts/server1")
    assert response.status_code == 401


def test_host_history_lists_all_runs_for_host(app, logged_in_client):
    seed_run(app, "server1", False, "disk_free", True)
    seed_run(app, "server1", True, "disk_free", False)

    response = logged_in_client.get("/api/hosts/server1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["hostname"] == "server1"
    assert len(data["runs"]) == 2
    assert all(run["steps"][0]["name"] == "disk_free" for run in data["runs"])
