"""Search module."""

import sys

from click import command, option, echo

from notelist_cli.auth import request, check_response
from notelist_cli.notebook import print_notebooks
from notelist_cli.note import print_notes


# Endpoints
search_ep = "/search"

# Option descriptions
des_search = "Search text."


@command()
@option("--s", required=True, help=des_search)
def search(s: str):
    """Search for notebooks and notes."""
    try:
        ep = f"{search_ep}/{s}"
        r = request("GET", ep, True)
        check_response(r)

        d = r.json()
        res = d.get("result")
        m = d.get("message")

        if res is None:
            raise Exception("Data not received.")

        # Result
        notebooks = res["notebooks"]
        notes = res["notes"]

        if len(notebooks) > 0:
            print("\n" + "Notebooks:")
            print_notebooks(notebooks)

        if len(notes) > 0:
            print("\n" + "Notes:")
            print_notes(notes)

        # Message
        if m is not None:
            echo("\n" + m)

        echo()
    except Exception as e:
        echo(f"Error: {e}")
        sys.exit(1)
