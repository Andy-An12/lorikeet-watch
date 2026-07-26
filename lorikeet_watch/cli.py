import click

from .auth import set_admin_credentials
from .db import init_db


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Initialized the database.")


@click.command("create-admin")
@click.argument("username")
@click.argument("password")
def create_admin_command(username, password):
    set_admin_credentials(username, password)
    click.echo(f"Admin user '{username}' set.")


def init_app(app):
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)
