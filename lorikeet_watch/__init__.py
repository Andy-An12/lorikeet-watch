import os
from pathlib import Path

from flask import Flask

from . import cli, db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        DATABASE=os.environ.get(
            "LORIKEET_WATCH_DB",
            str(Path(app.instance_path) / "lorikeet-watch.sqlite"),
        ),
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_HTTPONLY=True,
    )

    if test_config is not None:
        app.config.update(test_config)

    if not app.config.get("TESTING") and app.config["SECRET_KEY"] == "dev":
        app.logger.warning(
            "SECRET_KEY is set to the insecure default 'dev' — set the SECRET_KEY "
            "environment variable before deploying."
        )

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    cli.init_app(app)

    from . import dashboard, frontend, ingest, views_auth, views_settings
    app.register_blueprint(views_auth.bp, url_prefix="/api")
    app.register_blueprint(ingest.bp)
    app.register_blueprint(dashboard.bp, url_prefix="/api")
    app.register_blueprint(views_settings.bp, url_prefix="/api")
    app.register_blueprint(frontend.bp)

    return app
