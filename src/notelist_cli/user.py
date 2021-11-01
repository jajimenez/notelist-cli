"""User module."""

import sys
from typing import Optional

from click import group, option, echo

from notelist_cli.auth import get_user_id, request, check_response


# Endpoints
user_ep = "/users/user"

# Option descriptions
des_password_1 = "Password."
des_password_2 = "Repeat password"
des_name = "Name."
des_email = "E-mail."


@group()
def user():
    """Manage user."""
    pass


@user.command()
def get():
    """Get user."""
    try:
        _id = get_user_id()
        ep = f"{user_ep}/{_id}"

        r = request("GET", ep, True)
        check_response(r)

        res = r.json().get("result")

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


def put_user(
    password: Optional[str] = None, name: Optional[str] = None,
    email: Optional[str] = None
):
    """Put/update a user.

    :param password: Password.
    :param name: Name.
    :param email: E-mail.
    """
    data = {}

    if password is not None:
        data["password"] = password

    if name is not None:
        data["name"] = name

    if email is not None:
        data["email"] = email

    try:
        if len(data) == 0:
            raise Exception("No options specified. At least one is required.")

        # Get current data
        _id = get_user_id()
        ep = f"{user_ep}/{_id}"

        r = request("GET", ep, True)
        check_response(r)
        user = r.json().get("result")

        if user is None:
            raise Exception("Data not received.")

        # Get the fields that won't be updated except the password. For the API
        # update request, all fields except the password are required. The
        # password is optional.
        for k in ("name", "email"):
            if k not in data and k in user:
                data[k] = user[k]

        # Check if the user is an administrator. If the current user is an
        # administrator, we need to get the current values of the "username",
        # "admin" and "enabled" fields to avoid a validation error.
        if user["admin"]:
            for k in ("username", "admin", "enabled"):
                data[k] = user[k]

        # Update user
        r = request("PUT", ep, True, data)
        check_response(r)

        m = r.json().get("message")

        if m is not None:
            echo(m)
    except Exception as e:
        sys.exit(f"Error: {e}")


@option("--name", help=des_name)
@option("--email", help=des_email)
def update(name: Optional[str], email: Optional[str]):
    """Update user."""
    put_user(name=name, email=email)


@user.command()
@option(
    "--password", prompt=True, confirmation_prompt=des_password_2,
    hide_input=True, help=des_password_1
)
def updatepw(password: str):
    """Update user password."""
    put_user(password=password)
