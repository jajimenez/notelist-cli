"""User module."""

import sys

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
        echo(f"Error: {e}")
        sys.exit(1)


@user.command()
@option(
    "--password", prompt=True, confirmation_prompt=des_password_2,
    hide_input=True, help=des_password_1)
@option("--name", default="", prompt=True, help=des_name)
@option("--email", default="", prompt=True, help=des_email)
def update(password: str, name: str, email: str):
    """Update user.

    If the "--password" parameter is not set, its value is prompted and hidden.
    """
    data = {"password": password}

    if name != "":
        data["name"] = name

    if email != "":
        data["email"] = email

    try:
        # Get current data. If the current user is an administrator, we need to
        # send the current values of the "username", "admin" and "enabled"
        # fields to avoid a validation error.
        _id = get_user_id()
        ep = f"{user_ep}/{_id}"

        r = request("GET", ep, True)
        check_response(r)
        user = r.json().get("result")

        if user is None:
            raise Exception("Data not received.")

        k1 = "username"
        k2 = "admin"
        k3 = "enabled"

        # Check if the user is an administrator
        if user[k2]:
            data = data | {k1: user[k1], k2: user[k2], k3: user[k3]}

        # Update user
        r = request("PUT", ep, True, data)
        check_response(r)

        m = r.json().get("message")

        if m is not None:
            echo(m)
    except Exception as e:
        echo(f"Error: {e}")
        sys.exit(1)
