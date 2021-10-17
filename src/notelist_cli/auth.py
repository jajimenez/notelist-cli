"""Authentication module."""

from click import group, echo


@group()
def auth():
    """Make authentication requests."""
    pass


@auth.command()
def login():
    """Log in."""
    echo("Login")


@auth.command()
def logout():
    """Log out."""
    echo("Logout")
