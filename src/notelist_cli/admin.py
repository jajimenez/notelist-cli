"""Administration module."""

import sys

from click import group, option, confirmation_option, echo

from notelist_cli.auth import request, check_response


# Endpoints
users_ep = "/users/users"
user_ep = "/users/user"

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
    username = user.get("username")
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
        echo(f"Error: {e}")
        sys.exit(1)


@user.command()
@option("--id", prompt=True, help="User ID.")
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


def put_user(
    method: str, endpoint: str, username: str, password: str, admin: bool,
    enabled: bool, name: str, email: str
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

    if name != "":
        data["name"] = name

    if email != "":
        data["email"] = email

    try:
        r = request(method, endpoint, True, data)
        check_response(r)

        m = r.json().get("message")

        if m is not None:
            echo(m)
    except Exception as e:
        echo(f"Error: {e}")
        sys.exit(1)


@user.command()
@option("--username", prompt=True, help="Username.")
@option(
    "--password", prompt=True, confirmation_prompt="Repeat password",
    hide_input=True, help="Password."
)
@option(
    "--admin", prompt=True, default=False,
    help="Whether the user is an administrator or not."
)
@option(
    "--enabled", prompt=True, default=False,
    help="Whether the user is enabled or not.")
@option("--name", prompt=True, default="", help="Name.")
@option("--email", prompt=True, default="", help="E-mail.")
def create(
    username: str, password: str, admin: bool, enabled: bool, name: str,
    email: str
):
    """Create a user.

    The "--name" and "--email" parameters are optional and their default value
    is "False". If the "--password" parameter is not set, its value is prompted
    and hidden.
    """
    put_user("POST", user_ep, username, password, admin, enabled, name, email)


@user.command()
@option("--id", prompt=True, help="ID of the user to update.")
@option("--username", prompt=True, help="Username.")
@option(
    "--password", prompt=True, confirmation_prompt="Repeat password",
    hide_input=True, help="Password.")
@option(
    "--admin", prompt=True, default=False,
    help="Whether the user is an administrator or not."
)
@option(
    "--enabled", prompt=True, default=False,
    help="Whether the user is enabled or not.")
@option("--name", prompt=True, default="", help="Name.")
@option("--email", prompt=True, default="", help="E-mail.")
def update(
    id: str, username: str, password: str, admin: bool, enabled: bool,
    name: str, email: str
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
@option("--id", prompt=True, help="User ID.")
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
        echo(f"Error: {e}")
        sys.exit(1)
