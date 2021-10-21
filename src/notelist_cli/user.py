"""User module."""

import sys
from click import group, option, echo

from notelist_cli.auth import request, check_response


# Endpoints
ls_ep = "/users/users"
get_ep = "/users/user/{}"


def get_ls_header() -> str:
    """Return the header."""
    return (
        "ID" + (" " * 31) + "| Username" + (" " * 13) + "| Administrator | "
        "Enabled |\n")


def get_ls_user_line(user: dict) -> str:
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

        echo(get_ls_header())

        for u in res:
            echo(get_ls_user_line(u))

        if m is not None:
            echo("\n" + m)
    except Exception as e:
        echo(f"Error: {str(e)}")
        sys.exit(1)


@user.command()
@option("--id", prompt=True)
def get(id: str):
    """Get a user data.

    :param id: User ID.
    """
    try:
        ep = get_ep.format(id)
        r = request("GET", ep, True)
        check_response(r)

        d = r.json()
        res = d.get("result")

        if res is None:
            raise Exception("Data not received.")

        # User data
        _id = res.get("id")
        username = res.get("username")
        admin = str(int(res.get("admin")))
        enabled = str(int(res.get("enabled")))
        name = res.get("name")
        email = res.get("email")

        print("ID:" + (" " * 12) + _id)
        print("Username: " + (" " * 5) + username)
        print(f"Administrator: {admin}")
        print("Enabled:" + (" " * 7) + enabled)

        if name is not None:
            print(f"Name: {name}")

        if email is not None:
            print(f"E-mail: {email}")
    except Exception as e:
        echo(f"Error: {str(e)}")
        sys.exit(1)
