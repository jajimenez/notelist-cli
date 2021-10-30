"""Administration module."""

import sys
from typing import Optional

from click import group, option, confirmation_option, echo

from notelist_cli.auth import request, check_response


# Endpoints
users_ep = "/users/users"
user_ep = "/users/user"

# Option descriptions
des_user = "User ID."
des_username = "Username."
des_password_1 = "Password."
des_password_2 = "Repeat password"
des_admin = "Whether the user is an administrator or not."
des_enabled = "Whether the user is enabled or not."
des_name = "Name."
des_email = "E-mail."

# Messages
del_confirm = "Are you sure that you want to delete the user?"


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
    username = user["username"]
    c = len(username)

    if c <= 20:
        username = username + (" " * (20 - c))
    else:
        username = f"{username[:17]}..."

    admin = "Yes" if user["admin"] else "No "
    enabled = "Yes" if user["enabled"] else "No "

    line += username + " | "
    line += admin + (" " * 11) + "| "
    line += enabled + (" " * 5) + "|"

    return line


@group()
def admin():
    """Manage API."""
    pass


@admin.group()
def user():
    """Manage users."""
    pass


@user.command()
def ls():
    """List users."""
    try:
        r = request("GET", users_ep, True)
        check_response(r)

        d = r.json()
        users = d.get("result")

        if users is None:
            raise Exception("Data not received.")

        c = len(users)

        if c > 0:
            echo("\n" + get_ls_header())

            for u in users:
                echo(get_ls_user_line(u))

        s = "s" if c != 1 else ""
        echo(f"\n{c} user{s}\n")
    except Exception as e:
        sys.exit(f"Error: {e}")


@user.command()
@option("--id", required=True, help=des_user)
def get(id: str):
    """Get a user."""
    try:
        ep = f"{user_ep}/{id}"
        r = request("GET", ep, True)
        check_response(r)

        d = r.json()
        res = d.get("result")

        if res is None:
            raise Exception("Data not received.")

        # User data
        _id = res["id"]
        username = res["username"]
        admin = "Yes" if res["admin"] else "No"
        enabled = "Yes" if res["enabled"] else "No"
        name = res.get("name")
        email = res.get("email")
        created = res["created"].replace("T", " ")
        last_mod = res["last_modified"].replace("T", " ")

        echo("\nID:" + (" " * 12) + _id)
        echo("Username: " + (" " * 5) + username)
        echo(f"Administrator: {admin}")
        echo("Enabled:" + (" " * 7) + enabled)

        if name is not None:
            echo("Name:" + (" " * 10) + name)

        if email is not None:
            echo("E-mail:" + (" " * 8) + email)

        echo("Created:" + (" " * 7) + created)
        echo(f"Last modified: {last_mod}\n")
    except Exception as e:
        sys.exit(f"Error: {e}")


def put_user(
    method: str, endpoint: str, username: str, password: str, admin: bool,
    enabled: bool, name: Optional[str], email: Optional[str]
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
    data = {
        "username": username,
        "password": password,
        "admin": admin,
        "enabled": enabled
    }

    if name is not None:
        data["name"] = name

    if email is not None:
        data["email"] = email

    try:
        r = request(method, endpoint, True, data)
        check_response(r)

        m = r.json().get("message")

        if m is not None:
            echo(m)
    except Exception as e:
        sys.exit(f"Error: {e}")


@user.command()
@option("--username", required=True, help=des_username)
@option(
    "--password", prompt=True, confirmation_prompt=des_password_2,
    hide_input=True, help=des_password_1
)
@option("--admin", default=False, help=des_admin)
@option("--enabled", default=False, help=des_enabled)
@option("--name", help=des_name)
@option("--email", help=des_email)
def create(
    username: str, password: str, admin: bool, enabled: bool,
    name: Optional[str], email: Optional[str]
):
    """Create a user.

    The "--name" and "--email" parameters are optional and their default value
    is "False". If the "--password" parameter is not set, its value is prompted
    and hidden.
    """
    put_user("POST", user_ep, username, password, admin, enabled, name, email)


@user.command()
@option("--id", required=True, help=des_user)
@option("--username", required=True, help=des_username)
@option(
    "--password", prompt=True, confirmation_prompt=des_password_2,
    hide_input=True, help=des_password_1
)
@option("--admin", default=False, help=des_admin)
@option("--enabled", default=False, help=des_enabled)
@option("--name", help=des_name)
@option("--email", help=des_email)
def update(
    id: str, username: str, password: str, admin: bool, enabled: bool,
    name: Optional[str], email: Optional[str]
):
    """Update a user.

    The current user, if it's not an administrator, can update only its own
    data and cannot update the "--username", "--admin" and "--enabled"
    parameters.

    The "--name" and "--email" parameters are optional and their default value
    is "False". If the "--password" parameter is not set, its value is prompted
    and hidden.
    """
    ep = f"{user_ep}/{id}"
    put_user("PUT", ep, username, password, admin, enabled, name, email)


@user.command()
@option("--id", required=True, help=des_user)
@confirmation_option(prompt=del_confirm)
def delete(id: str):
    """Delete a user."""
    try:
        ep = f"{user_ep}/{id}"
        r = request("DELETE", ep, True)
        check_response(r)

        m = r.json().get("message")

        if m is not None:
            echo(m)
    except Exception as e:
        sys.exit(f"Error: {e}")
