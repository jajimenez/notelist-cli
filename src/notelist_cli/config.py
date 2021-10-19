"""Configuration module."""

from click import command, option
from userconf import Userconf


# Settings
app_id = "notelist_cli"
_api_url = "api_url"

uc = Userconf(app_id)


@command()
@option("--api-url", prompt=True)
def config(api_url: str):
    """Configure the CLI."""
    uc.set(_api_url, api_url)
