"""Authentication module."""

import sys
from typing import Optional

import requests as req
from click import group, option, echo
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
acc_tok_error = 'Access token not found. Please run "notelist-cli auth login".'


def get_api_url() -> str:
    """Get the API URL.

    An `Exception` is raised if the API URL is not found.

    :returns: API URL.
    """
    _api_url = uc.get(api_url)

    if _api_url is None:
        raise Exception(api_url_error)

    return _api_url


def get_acc_tok() -> str:
    """Get the access token.

    An `Exception` is raised if the access token is not found.

    :returns: Access token.
    """
    _api_url = uc.get(api_url)

    if _api_url is None:
        raise Exception(api_url_error)

    return _api_url


def refresh_access_token() -> req.Response:
    """Update the access token with a new, not fresh, token.

    :returns: Request response.
    """
    _api_url = get_api_url()
    old_at = get_acc_tok()

    url = f"{_api_url}/{refresh_ep}"
    headers = {"Authorization": f"Bearer {old_at}"}
    r = req.get(url, headers=headers)

    # Update access token
    if r.status_code == 200:
        new_at = r.json()["result"]["access_token"]
        uc.set(acc_tok, new_at)

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
    url = f"{_api_url}/{endpoint}"
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
    if r.json().get("message_type") == "error_expired_token" and retry:
        r = refresh_access_token()

        if r.status_code == 200:
            r = request(method, endpoint, auth, data, False)

    return r


@group()
def auth():
    """Do an authentication operation."""
    pass


@auth.command()
@option("--username", prompt=True)
@option("--password", prompt=True, hide_input=True)
def login(username: str, password: str):
    """Log in."""
    try:
        # Make request
        _api_url = get_api_url()
        url = f"{_api_url}/{login_ep}"

        data = {"username": username, "password": password}
        r = req.post(url, json=data)
        d = r.json()
        res = d["result"]

        # Save credentials
        uc.set(user_id, res["user_id"])
        uc.set(acc_tok, res["access_token"])
        uc.set(ref_tok, res["refresh_token"])

        # Print response message
        echo(d["message"])
    except Exception as e:
        sys.exit(f"Error: {str(e)}")


@auth.command()
def logout():
    """Log out."""
    try:
        # Make request
        _api_url = get_api_url()
        url = f"{_api_url}/{logout_ep}"

        at = uc.get(acc_tok)
        headers = {"Authorization": f"Bearer {at}"}

        r = req.get(url, headers=headers)

        # Delete credentials
        for i in (user_id, acc_tok, ref_tok):
            uc.delete(i)

        # Print response message
        echo(r.json()["message"])
    except Exception as e:
        sys.exit(f"Error: {str(e)}")
