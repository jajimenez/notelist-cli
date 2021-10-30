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

        if res is None:
            raise Exception("Data not received.")

        # Result
        notebooks = res["notebooks"]
        notes = res["notes"]

        # Print notebooks found
        c = len(notebooks)
        s1 = "s" if c != 1 else ""
        s2 = ":" if c > 0 else ""

        echo(f"\n{c} notebook{s1} found{s2}")

        if c > 0:
            print_notebooks(notebooks)

        # Print notes found
        c = len(notes)
        s1 = "s" if c != 1 else ""
        s2 = ":" if c > 0 else ""

        echo(f"\n{c} note{s1} found{s2}")

        if c > 0:
            print_notes(notes)

        echo()
    except Exception as e:
        sys.exit(f"Error: {e}")
