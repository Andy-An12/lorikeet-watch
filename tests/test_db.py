from lorikeet_watch.db import get_db


def test_init_db_creates_tables(app):
    with app.app_context():
        db = get_db()
        tables = {
            row["name"]
            for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    assert {"runs", "steps", "settings"} <= tables
