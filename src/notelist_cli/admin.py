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
        "Enabled\n"
    )


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
    line += enabled

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
            echo(get_ls_header())

            for u in users:
                echo(get_ls_user_line(u))

            echo()

        s = "s" if c != 1 else ""
        echo(f"{c} user{s}")
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

        echo("ID:" + (" " * 12) + _id)
        echo("Username: " + (" " * 5) + username)
        echo(f"Administrator: {admin}")
        echo("Enabled:" + (" " * 7) + enabled)

        if name is not None:
            echo("Name:" + (" " * 10) + name)

        if email is not None:
            echo("E-mail:" + (" " * 8) + email)

        echo("Created:" + (" " * 7) + created)
        echo(f"Last modified: {last_mod}")
    except Exception as e:
        sys.exit(f"Error: {e}")


@user.command()
@option("--username", required=True, help=des_username)
@option(
    "--password", prompt=True, confirmation_prompt=des_password_2,
    hide_input=True, help=des_password_1
)
@option("--admin", type=bool, help=des_admin)
@option("--enabled", type=bool, help=des_enabled)
@option("--name", help=des_name)
@option("--email", help=des_email)
def create(
    username: str, password: str, admin: Optional[bool],
    enabled: Optional[bool], name: Optional[str], email: Optional[str]
):
    """Create a user."""
    data = {
        "username": username,
        "password": password
    }

    if admin is not None:
        data["admin"] = admin

    if enabled is not None:
        data["enabled"] = enabled

    if name is not None:
        data["name"] = name

    if email is not None:
        data["email"] = email

    try:
        r = request("POST", user_ep, True, data)
        check_response(r)

        m = r.json().get("message")

        if m is not None:
            echo(m)
    except Exception as e:
        sys.exit(f"Error: {e}")


def put_user(
    _id: str, username: Optional[str] = None, password: Optional[str] = None,
    admin: Optional[bool] = None, enabled: Optional[bool] = None,
    name: Optional[str] = None, email: Optional[str] = None
):
    """Put/update a user.

    :param _id: User ID.
    :param username: Username.
    :param password: Password.
    :param admin: Whether the user is an administrator or not.
    :param enabled: Whether the user is enabled or not.
    :param name: Name.
    :param email: E-mail.
    """
    data = {}

    if username is not None:
        data["username"] = username

    if password is not None:
        data["password"] = password

    if admin is not None:
        data["admin"] = admin

    if enabled is not None:
        data["enabled"] = enabled

    if name is not None:
        data["name"] = name

    if email is not None:
        data["email"] = email

    try:
        if len(data) == 0:
            raise Exception("No options specified. At least one is required.")

        # Get current data
        ep = f"{user_ep}/{_id}"

        r = request("GET", ep, True)
        check_response(r)
        user = r.json().get("result")

        if user is None:
            raise Exception("Data not received.")

        # Get the fields that won't be updated except the password. For the API
        # update request, all fields except the password are required. The
        # password is optional.
        for k in ("username", "admin", "enabled", "name", "email"):
            if k in data and data[k] == "":
                data.pop(k)
            elif k not in data and k in user:
                data[k] = user[k]

        # Update user
        r = request("PUT", ep, True, data)
        check_response(r)

        m = r.json().get("message")

        if m is not None:
            echo(m)
    except Exception as e:
        sys.exit(f"Error: {e}")


@user.command()
@option("--id", required=True, help=des_user)
@option("--username", help=des_username)
@option("--admin", type=bool, help=des_admin)
@option("--enabled", type=bool, help=des_enabled)
@option("--name", help=des_name)
@option("--email", help=des_email)
def update(
    id: str, username: Optional[str], admin: Optional[bool],
    enabled: Optional[bool], name: Optional[str], email: Optional[str]
):
    """Update a user."""
    put_user(
        id, username=username, admin=admin, enabled=enabled, name=name,
        email=email
    )


@user.command()
@option(
    "--password", prompt=True, confirmation_prompt=des_password_2,
    hide_input=True, help=des_password_1
)
def updatepw(password: str):
    """Update a user password."""
    put_user(password=password)


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
