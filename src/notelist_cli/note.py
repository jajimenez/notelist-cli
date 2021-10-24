"""Note module."""

import sys

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
    return (
        "ID" + (" " * 31) + "| Title" + (" " * 16) + "| Tags" + (" " * 16) +
        "\n"
    )


def get_ls_note_line(note: dict) -> str:
    """Get a string representing a note in the Note Ls command.

    :param note: Note data.
    :returns: Note string.
    """
    line = note["id"] + " | "
    title = note.get("title", "Untitled")
    tags = note.get("tags")

    c = len(title)

    if c <= 20:
        title = title + (" " * (20 - c))
    else:
        title = f"{title[:17]}..."

    line += title + " | "

    if tags is not None:
        tags = ", ".join(tags)
        c = len(tags)

        if c <= 20:
            tags = tags + (" " * (20 - c))
        else:
            tags = f"{tags[:17]}..."

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
    echo("\n" + get_ls_header())

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
    nid: str, archived: bool, tags: str, notags: bool, lastmod: bool, asc: bool
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
        res = d.get("result")
        m = d.get("message")

        if res is None:
            raise Exception("Data not received.")

        print_notes(res)

        # Message
        if m is not None:
            echo("\n" + m)

        echo()
    except Exception as e:
        echo(f"Error: {e}")
        sys.exit(1)


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
        echo("\nID:" + (" " * 12) + _id)
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

        echo()
    except Exception as e:
        echo(f"Error: {e}")
        sys.exit(1)


def put_note(
    method: str, endpoint: str, notebook_id: str, archived: bool, title: str,
    body: str, tags: str
):
    """Put (create or update) a note.

    :param method: Request method ("POST" or "PUT").
    :param endpoint: Request endpoint.
    :param notebook_id: Notebook ID.
    :param archived: Whether the note is archived or not.
    :param title: Title.
    :param body: Body.
    :param tags: Comma separated tags. E.g. "tag1,tag2".
    """
    data = {"notebook_id": notebook_id, "archived": archived}

    if title != "":
        data["title"] = title

    if body != "":
        data["body"] = body

    if tags != "":
        tags = tags.replace(" ", "").split(",")
        data["tags"] = tags

    try:
        r = request(method, endpoint, True, data)
        check_response(r)

        m = r.json().get("message")

        if m is not None:
            echo(m)
    except Exception as e:
        echo(f"Error: {e}")
        sys.exit(1)


@note.command()
@option("--nid", prompt=True, help=des_notebook)
@option("--archived", default=False, prompt=True, help=des_arc)
@option("--title", default="", prompt=True, help=des_title)
@option("--body", default="", prompt=True, help=des_body)
@option("--tags", default="", prompt=True, help=des_tags)
def create(nid: str, archived: bool, title: str, body: str, tags: str):
    """Create a note."""
    put_note("POST", note_ep, nid, archived, title, body, tags)


@note.command()
@option("--id", prompt=True, help=des_note)
@option("--nid", prompt=True, help=des_notebook)
@option("--archived", default=False, prompt=True, help=des_arc)
@option("--title", default="", prompt=True, help=des_title)
@option("--body", default="", prompt=True, help=des_body)
@option("--tags", default="", prompt=True, help=des_tags)
def update(
    id: str, nid: str, archived: bool, title: str, body: str, tags: str
):
    """Update a note."""
    ep = f"{note_ep}/{id}"
    put_note("PUT", ep, nid, archived, title, body, tags)


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
        echo(f"Error: {e}")
        sys.exit(1)
