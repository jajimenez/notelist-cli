"""Notelist CLI.

Notelist CLI is a command line interface for the Notelist API.
"""

from click import group

from notelist_cli.config import config
from notelist_cli.admin import admin
from notelist_cli.auth import auth
from notelist_cli.user import user
from notelist_cli.notebook import notebook
from notelist_cli.note import note


__version__ = "0.1.0"


@group()
def cli():
    """Notelist CLI is a command line interface for the Notelist API."""
    pass


cli.add_command(config)
cli.add_command(admin)
cli.add_command(auth)
cli.add_command(user)
cli.add_command(notebook)
cli.add_command(note)
