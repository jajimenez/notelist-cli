"""User module."""

import sys
from click import group, option, echo

from notelist_cli.auth import request, check_response


# Endpoints
users_ep = "/users/users"
user_ep = "/users/user"


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
        r = request("GET", users_ep, True)
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
    """Get a user.

    :param id: User ID.
    """
    try:
        ep = f"{user_ep}/{id}"
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
            print("Name:" + (" " * 10) + name)

        if email is not None:
            print("E-mail:" + (" " * 8) + email)
    except Exception as e:
        echo(f"Error: {str(e)}")
        sys.exit(1)


@user.command()
@option("--username", prompt=True)
@option("--password", prompt=True, hide_input=True)
@option("--admin", prompt=True, default=False)
@option("--enabled", prompt=True, default=False)
@option("--name", prompt=True, default="")
@option("--email", prompt=True, default="")
def create(
    username: str, password: str, admin: bool, enabled: bool, name: str,
    email: str
):
    """Create a user.

    :param username: Username.
    :param password: Password.
    :param admin: Whether the user is an administrator or not.
    :param enabled: Whether the user is enabled or not.
    :param name: Name.
    :param email: E-mail.
    """
    data = {
        "username": username,
        "password": password,
        "admin": admin,
        "enabled": enabled
    }

    if name != "":
        data["name"] = name

    if email != "":
        data["email"] = email

    try:
        r = request("POST", user_ep, True, data)
        check_response(r)
    except Exception as e:
        echo(f"Error: {str(e)}")
        sys.exit(1)
