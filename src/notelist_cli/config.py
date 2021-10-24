"""Configuration module."""

from click import command, option
from userconf import Userconf


# Option descriptions
des_api_url = "Notelist API URL."

# Settings
app_id = "notelist_cli"
_api_url = "api_url"

uc = Userconf(app_id)


@command()
@option("--apiurl", prompt=True, help=des_api_url)
def config(apiurl: str):
    """Configure CLI."""
    uc.set(_api_url, apiurl)
