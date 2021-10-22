"""Authentication module."""

import sys
from typing import Optional

import requests as req
from click import group, option, echo
from requests.models import Response
from userconf import Userconf


# Settings
app_id = "notelist_cli"
api_url = "api_url"
user_id = "user_id"
acc_tok = "access_token"
ref_tok = "refresh_token"

uc = Userconf(app_id)

# Endpoints
login_ep = "/auth/login"
refresh_ep = "/auth/refresh"
logout_ep = "/auth/logout"

# Error messages
api_url_error = 'API URL not found. Please run "notelist-cli config".'
login_me = 'Please run "notelist-cli auth login".'
uid_error = f"User ID not found. {login_me}"
acc_tok_error = f"Access token not found. {login_me}"
ref_tok_error = f"Refresh token not found. {login_me}"


def get_api_url() -> str:
    """Get the API URL.

    An `Exception` is raised if the API URL is not found.

    :returns: API URL.
    """
    _api_url = uc.get(api_url)

    if _api_url is None:
        raise Exception(api_url_error)

    return _api_url


def get_user_id() -> str:
    """Get the user ID.

    An `Exception` is raised if the user ID is not found.

    :returns: User ID.
    """
    _id = uc.get(user_id)

    if _id is None:
        raise Exception(uid_error)

    return _id


def get_acc_tok() -> str:
    """Get the access token.

    An `Exception` is raised if the access token is not found.

    :returns: Access token.
    """
    token = uc.get(acc_tok)

    if token is None:
        raise Exception(acc_tok_error)

    return token


def get_ref_tok() -> str:
    """Get the refresh token.

    An `Exception` is raised if the access token is not found.

    :returns: Access token.
    """
    token = uc.get(ref_tok)

    if token is None:
        raise Exception(ref_tok_error)

    return token


def refresh_access_token() -> req.Response:
    """Update the access token with a new, not fresh, token.

    :returns: Request response.
    """
    _api_url = get_api_url()
    ref = get_ref_tok()

    url = f"{_api_url}{refresh_ep}"
    headers = {"Authorization": f"Bearer {ref}"}
    r = req.get(url, headers=headers)

    # Update access token
    if r.status_code == 200:
        acc = r.json()["result"]["access_token"]
        uc.set(acc_tok, acc)

    return r


def request(
    method: str, endpoint: str, auth: bool = False,
    data: Optional[dict] = None, retry: bool = True
) -> req.Response:
    """Make a HTTP request.

    :param method: Request method ("GET", "POST", "PUT" or "DELETE").
    :param endpoint: Relative endpoint URL (e.g. "/users/users").
    :param auth: Whether the request is authenticated or not.
    :param data: Request data.
    :param retry: Whether to retry the request or not if the access token is
    expired.
    :returns: Request response.
    """
    _api_url = get_api_url()
    url = f"{_api_url}{endpoint}"
    args = {}

    # Headers
    if auth:
        at = get_acc_tok()
        args["headers"] = {"Authorization": f"Bearer {at}"}

    # Data
    if data is not None:
        args["json"] = data

    # Make request
    r = req.request(method, url, **args)

    # If the access token is expired, we make the request again with a new, not
    # fresh, access token.
    k = "message_type"
    t = "error_expired_token"

    if r.json().get(k) == t and retry:
        r = refresh_access_token()

        if r.status_code == 200:
            r = request(method, endpoint, auth, data, False)

    return r


def check_response(r: Response):
    """Check a response and quit the application if there is an error.

    :param r: Request response.
    """
    data = r.json()

    m = data.get("message")
    t = data.get("message_type")

    if r.status_code != 200:
        if t in ("error_expired_token", "error_not_fresh_token"):
            m += ". " + login_me

        echo(m)
        sys.exit(1)


@group()
def auth():
    """Log in/out."""
    pass


@auth.command()
@option("--username", prompt=True, help="Username.")
@option("--password", prompt=True, hide_input=True, help="Password.")
def login(username: str, password: str):
    """Log in."""
    try:
        # Make request
        _api_url = get_api_url()
        url = f"{_api_url}{login_ep}"

        data = {"username": username, "password": password}
        r = req.post(url, json=data)
        d = r.json()
        res = d.get("result")
        m = d.get("message")

        if res is not None:
            # Save credentials
            uc.set(user_id, res["user_id"])
            uc.set(acc_tok, res["access_token"])
            uc.set(ref_tok, res["refresh_token"])

        # Print response message
        if m is not None:
            echo(m)
    except Exception as e:
        echo(f"Error: {e}")
        sys.exit(1)


@auth.command()
def logout():
    """Log out."""
    try:
        # Make request
        _api_url = get_api_url()
        url = f"{_api_url}{logout_ep}"

        at = uc.get(acc_tok)
        headers = {"Authorization": f"Bearer {at}"}

        r = req.get(url, headers=headers)
        m = r.json().get("message")

        # Delete credentials
        for i in (user_id, acc_tok, ref_tok):
            uc.delete(i)

        # Print response message
        if m is not None:
            echo(m)
    except Exception as e:
        echo(f"Error: {e}")
        sys.exit(1)
