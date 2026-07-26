from flask import Blueprint, jsonify

from .auth import login_required
from .db import get_db

bp = Blueprint("dashboard", __name__)


@bp.route("/dashboard")
@login_required
def index():
    db = get_db()
    rows = db.execute(
        """
        SELECT r.* FROM runs r
        INNER JOIN (
            SELECT hostname, MAX(id) AS max_id FROM runs GROUP BY hostname
        ) latest ON r.hostname = latest.hostname AND r.id = latest.max_id
        ORDER BY r.hostname
        """
    ).fetchall()
    return jsonify(
        {
            "runs": [
                {
                    "hostname": row["hostname"],
                    "has_errors": bool(row["has_errors"]),
                    "created_at": row["created_at"],
                }
                for row in rows
            ]
        }
    )


@bp.route("/hosts/<hostname>")
@login_required
def host_history(hostname):
    db = get_db()
    runs = db.execute(
        "SELECT * FROM runs WHERE hostname = ? ORDER BY id DESC",
        (hostname,),
    ).fetchall()

    run_ids = [r["id"] for r in runs]
    steps_by_run = {}
    if run_ids:
        placeholders = ",".join("?" for _ in run_ids)
        step_rows = db.execute(
            f"SELECT * FROM steps WHERE run_id IN ({placeholders})",
            run_ids,
        ).fetchall()
        for step in step_rows:
            steps_by_run.setdefault(step["run_id"], []).append(step)

    return jsonify(
        {
            "hostname": hostname,
            "runs": [
                {
                    "id": run["id"],
                    "has_errors": bool(run["has_errors"]),
                    "created_at": run["created_at"],
                    "steps": [
                        {
                            "name": step["name"],
                            "pass": bool(step["pass"]),
                            "output": step["output"],
                            "error": step["error"],
                            "duration": step["duration"],
                        }
                        for step in steps_by_run.get(run["id"], [])
                    ],
                }
                for run in runs
            ],
        }
    )
