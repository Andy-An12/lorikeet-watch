from pathlib import Path

from flask import Blueprint, send_from_directory

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend" / "out"

bp = Blueprint("frontend", __name__)


@bp.route("/", defaults={"path": ""})
@bp.route("/<path:path>")
def serve(path):
    candidates = [path, f"{path}.html", f"{path}/index.html"] if path else ["index.html"]
    for candidate in candidates:
        if (FRONTEND_DIR / candidate).is_file():
            return send_from_directory(FRONTEND_DIR, candidate)
    return send_from_directory(FRONTEND_DIR, "index.html")
