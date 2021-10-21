"""User module."""

import sys
from click import group, option, Choice, echo

from notelist_cli.auth import request, check_response


# Endpoints
users_ep = "/users/users"
user_ep = "/users/user"


def get_ls_header() -> str:
    """Get the header in the User Ls command.

    :returns: Header.
    """
    return (
        "ID" + (" " * 31) + "| Username" + (" " * 13) + "| Administrator | "
        "Enabled |\n")


def get_ls_user_line(user: dict) -> str:
    """Get a string representing a user in the User Ls command.

    :param user: User data.
    :returns: User string.
    """
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


def put_user(
    method: str, endpoint: str, username: str, password: str, admin: str,
    enabled: str, name: str, email: str
):
    """Put (create or update) a user.

    :param method: Request method ("POST" or "PUT").
    :param endpoint: Request endpoint.
    :param username: Username.
    :param password: Password.
    :param admin: Whether the user is an administrator or not.
    :param enabled: Whether the user is enabled or not.
    :param name: Name.
    :param email: E-mail.
    """
    data = {}

    if username != "":
        data["username"] = username

    if password != "":
        data["password"] = password

    if admin != "":
        data["admin"] = bool(int(admin))

    if enabled != "":
        data["enabled"] = bool(int(enabled))

    if name != "":
        data["name"] = name

    if email != "":
        data["email"] = email

    try:
        r = request(method, endpoint, True, data)
        check_response(r)
    except Exception as e:
        echo(f"Error: {str(e)}")
        sys.exit(1)


@user.command()
@option("--username", prompt=True, help="Username")
@option("--password", prompt=True, hide_input=True, help="Password")
@option(
    "--admin", prompt=True, type=Choice(["0", "1"]), default="0",
    help="Whether the user is an administrator or not."
)
@option(
    "--enabled", prompt=True, type=Choice(["0", "1"]), default="0",
    help="Whether the user is enabled or not."
)
@option("--name", prompt=True, default="", help="Name")
@option("--email", prompt=True, default="", help="E-mail")
def create(
    username: str, password: str, admin: str, enabled: str, name: str,
    email: str
):
    """Create a user.

    "name" and "email" parameters are optional and can be left empty in order
    to not update them.
    """
    put_user("POST", user_ep, username, password, admin, enabled, name, email)


@user.command()
@option("--id", prompt=True, help="ID of the user to update.")
@option("--username", prompt=True, default="", help="New username.")
@option(
    "--password", prompt=True, default="", hide_input=True,
    help="New password."
)
@option(
    "--admin", prompt=True, type=Choice(["", "0", "1"]), default="",
    help="New Admin (whether the user is an administrator or not)."
)
@option(
    "--enabled", prompt=True, type=Choice(["", "0", "1"]), default="",
    help="New Enabled (whether the user is enabled or not)."
)
@option("--name", prompt=True, default="", help="New name.")
@option("--email", prompt=True, default="", help="New e-mail.")
def update(
    id: str, username: str, password: str, admin: str, enabled: str, name: str,
    email: str
):
    """Update a user.

    All parameters are optional and can be left empty in order to not update
    them.

    "username", "admin" and "enabled" parameters can be updated only by
    administrators users. If the user doing the update operation is not an
    administrator and tries to update any of these fields, an Unknown Field
    error is returned.
    """
    ep = f"{user_ep}/{id}"
    put_user("PUT", ep, username, password, admin, enabled, name, email)
