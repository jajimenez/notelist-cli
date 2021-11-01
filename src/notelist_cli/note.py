"""Note module."""

import sys
from typing import Optional

from click import group, option, confirmation_option, echo

from notelist_cli.auth import request, check_response


# Endpoints
notebook_ep = "/notebooks/notebook"
notes_ep = "/notes/notes"
note_ep = "/notes/note"

# Option descriptions
des_notebook = "Notebook ID."
des_note = "Note ID."
des_title = "Title."
des_body = "Body."
des_tags = 'Comma separated tags. E.g. "tag1,tag2".'
des_asc = "Whether the order is ascending or descending."
des_arc = "Whether the note is archived or not."
des_ls_arc = "Filter notes by their state (archived/active)."
des_ls_tags = (
    'Comma separated tags to filter the notes with. E.g. "tag1,tag2".'
)
des_ls_no_tags = (
    'When filtering with "--tags", whether to get notes with no tags or not. '
    'This filter only applies if "--tags" is set.'
)
des_ls_last_mod = (
    "Whether to sort the notes by their Last Modified date-time or by their "
    "Created date-time."
)

# Messages
del_confirm = "Are you sure that you want to delete the note?"


def get_ls_header() -> str:
    """Get the header in the Note Ls command.

    :returns: Header.
    """
    return "ID" + (" " * 31) + "| Title" + (" " * 36) + "| Tags\n"


def get_ls_note_line(note: dict) -> str:
    """Get a string representing a note in the Note Ls command.

    :param note: Note data.
    :returns: Note string.
    """
    line = note["id"] + " | "
    title = note.get("title", "Untitled")
    tags = note.get("tags")

    c = len(title)

    if c <= 40:
        title = title + (" " * (40 - c))
    else:
        title = f"{title[:37]}..."

    line += title + " | "

    if tags is not None:
        tags = ", ".join(tags)
        c = len(tags)

        if c <= 40:
            tags = tags + (" " * (40 - c))
        else:
            tags = f"{tags[:37]}..."

        line += tags

    return line


@group()
def note():
    """Manage notes."""
    pass


def print_notes(notes: list[dict]):
    """Print a note list.

    :param notes: Notes.
    """
    echo(get_ls_header())

    for n in notes:
        echo(get_ls_note_line(n))


@note.command()
@option("--nid", required=True, help=des_notebook)
@option("--archived", default=False, help=des_ls_arc)
@option("--tags", help=des_ls_tags)
@option("--notags", default=False, help=des_ls_no_tags)
@option("--lastmod", default=True, help=des_ls_last_mod)
@option("--asc", default=False, help=des_asc)
def ls(
    nid: str, archived: bool, tags: Optional[str], notags: bool, lastmod: bool,
    asc: bool
):
    """List all the notes of a notebook that match a filter."""
    ep = f"{notes_ep}/{nid}"

    data = {
        "archived": archived,
        "last_mod": lastmod,
        "asc": asc
    }

    if tags is not None:
        tags = tags.replace(" ", "")
        tags = tags.split(",") if tags != "" else []

        data["tags"] = tags
        data["no_tags"] = notags

    try:
        r = request("POST", ep, True, data=data)
        check_response(r)

        d = r.json()
        notes = d.get("result")

        if notes is None:
            raise Exception("Data not received.")

        c = len(notes)

        if c > 0:
            print_notes(notes)
            echo()

        s = "s" if c != 1 else ""
        echo(f"{c} note{s}")
    except Exception as e:
        sys.exit(f"Error: {e}")


@note.command()
@option("--id", required=True, help=des_note)
def get(id: str):
    """Get a note."""
    try:
        # Get note
        ep = f"{note_ep}/{id}"
        r = request("GET", ep, True)
        check_response(r)

        d = r.json()
        res = d.get("result")

        if res is None:
            raise Exception("Data not received.")

        _id = res["id"]
        nb_id = res["notebook_id"]
        archived = "Yes" if res["archived"] else "No"
        title = res.get("title")
        tags = res.get("tags")
        created = res["created"].replace("T", " ")
        last_mod = res["last_modified"].replace("T", " ")
        body = res.get("body")

        # Get notebook name
        ep = f"{notebook_ep}/{nb_id}"
        r = request("GET", ep, True)
        check_response(r)

        d = r.json()
        res = d.get("result")

        if res is None:
            raise Exception("Data not received.")

        nb_name = res["name"]

        # Print note
        echo("ID:" + (" " * 12) + _id)
        echo("Notebook ID:" + (" " * 3) + nb_id)
        echo(f"Notebook name: {nb_name}")
        echo("Archived:" + (" " * 6) + archived)

        if title is not None:
            echo("Title:" + (" " * 9) + title)

        if tags is not None:
            tags = ", ".join(tags)
            echo("Tags:" + (" " * 10) + tags)

        echo("Created:" + (" " * 7) + created)
        echo(f"Last modified: {last_mod}")

        if body is not None:
            echo("\n" + body)
    except Exception as e:
        sys.exit(f"Error: {e}")


@note.command()
@option("--nid", required=True, help=des_notebook)
@option("--archived", type=bool, help=des_arc)
@option("--title", help=des_title)
@option("--body", help=des_body)
@option("--tags", help=des_tags)
def create(
    nid: str, archived: bool, title: Optional[str], body: Optional[str],
    tags: Optional[str]
):
    """Create a note."""
    data = {"notebook_id": nid}

    if archived is not None:
        data["archived"] = archived

    if title is not None:
        data["title"] = title

    if body is not None:
        data["body"] = body

    if tags is not None:
        tags = tags.replace(" ", "").split(",")
        data["tags"] = tags

    try:
        r = request("POST", note_ep, True, data)
        check_response(r)

        m = r.json().get("message")

        if m is not None:
            echo(m)
    except Exception as e:
        sys.exit(f"Error: {e}")


@note.command()
@option("--id", required=True, help=des_note)
@option("--nid", help=des_notebook)
@option("--archived", type=bool, help=des_arc)
@option("--title", help=des_title)
@option("--body", help=des_body)
@option("--tags", help=des_tags)
def update(
    id: str, nid: str, archived: Optional[bool], title: Optional[str],
    body: Optional[str], tags: Optional[str]
):
    """Update a note."""
    data = {}

    if nid is not None:
        data["notebook_id"] = nid

    if archived is not None:
        data["archived"] = archived

    if title is not None:
        data["title"] = title

    if body is not None:
        data["body"] = body

    if tags is not None:
        tags = tags.replace(" ", "").split(",")
        data["tags"] = tags

    try:
        if len(data) == 0:
            raise Exception("No options specified. At least one is required.")

        # Get current data
        ep = f"{note_ep}/{id}"

        r = request("GET", ep, True)
        check_response(r)
        note = r.json().get("result")

        if note is None:
            raise Exception("Data not received.")

        # Get the fields that won't be updated. For the API update request, all
        # fields are required.
        for k in ("notebook_id", "archived", "title", "body", "tags"):
            if k not in data and k in note:
                data[k] = note[k]

        # Update note
        r = request("PUT", ep, True, data)
        check_response(r)

        m = r.json().get("message")

        if m is not None:
            echo(m)
    except Exception as e:
        sys.exit(f"Error: {e}")


@note.command()
@option("--id", required=True, help=des_note)
@confirmation_option(prompt=del_confirm)
def delete(id: str):
    """Delete a note."""
    try:
        ep = f"{note_ep}/{id}"
        r = request("DELETE", ep, True)
        check_response(r)

        m = r.json().get("message")

        if m is not None:
            echo(m)
    except Exception as e:
        sys.exit(f"Error: {e}")
