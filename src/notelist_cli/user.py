"""User module."""

import sys
from click import group, echo

from notelist_cli.auth import request, check_response


# Endpoints
ls_ep = "/users/users"


def get_header() -> str:
    """Return the header."""
    return (
        "ID" + (" " * 31) + "| Username" + (" " * 13) + "| Administrator | "
        "Enabled |\n")


def get_user_line(user: dict) -> str:
    """Return a string representing a user."""
    line = user["id"] + " | "

    username = user.get("username", "")
    c = len(username)

    if c <= 20:
        username = username + (" " * (20 - c))
    else:
        username = f"{username[:17]}..."

    line += username + " | "
    line += str(int(user["admin"])) + (" " * 13) + "| "
    line += str(int(user["enabled"])) + (" " * 7) + "|"

    return line


@group()
def user():
    """Manage users."""
    pass


@user.command()
def ls():
    """List all the users."""
    try:
        r = request("GET", ls_ep, True)
        check_response(r)

        d = r.json()
        res = d.get("result")
        m = d.get("message")

        if res is None:
            raise Exception("Data not received.")

        echo(get_header())

        for u in res:
            echo(get_user_line(u))

        if m is not None:
            echo("\n" + m)
    except Exception as e:
        sys.exit(f"Error: {str(e)}")
