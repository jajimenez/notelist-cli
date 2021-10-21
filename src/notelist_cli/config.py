"""Configuration module."""

from click import command, option
from userconf import Userconf


# Settings
app_id = "notelist_cli"
_api_url = "api_url"

uc = Userconf(app_id)


@command()
@option("--api-url", prompt=True, help="Notelist API URL.")
def config(api_url: str):
    """Configure this application."""
    uc.set(_api_url, api_url)
