"""Notebook module."""

import sys

from click import group, option, confirmation_option, echo

from notelist_cli.auth import request, check_response


# Endpoints
notebooks_ep = "/notebooks/notebooks"
notebook_ep = "/notebooks/notebook"

# Option descriptions
des_notebook = "Notebook ID."
des_name = "Name."
des_tag_colors = 'Tag colors. E.g. "tag1=color1,tag2=color2".'

# Messages
del_confirm = "Are you sure that you want to delete the notebook?"


def get_ls_header() -> str:
    """Get the header in the Notebook Ls command.

    :returns: Header.
    """
    return "ID" + (" " * 31) + "| Name\n"


def get_ls_notebook_line(notebook: dict) -> str:
    """Get a string representing a notebook in the Notebook Ls command.

    :param notebook: Notebook data.
    :returns: Notebook string.
    """
    line = notebook["id"] + " | "
    name = notebook.get("name")
    c = len(name)

    if c > 20:
        name = f"{name[:17]}..."

    line += name
    return line


@group()
def notebook():
    """Manage notebooks."""
    pass


def print_notebooks(notebooks: list[dict]):
    """Print a notebook list.

    :param notebooks: Notebooks.
    """
    echo("\n" + get_ls_header())

    for n in notebooks:
        echo(get_ls_notebook_line(n))


@notebook.command()
def ls():
    """List all the notebooks of the current user."""
    try:
        r = request("GET", notebooks_ep, True)
        check_response(r)

        d = r.json()
        res = d.get("result")
        m = d.get("message")

        if res is None:
            raise Exception("Data not received.")

        print_notebooks(res)

        # Message
        if m is not None:
            echo("\n" + m)

        echo()
    except Exception as e:
        echo(f"Error: {e}")
        sys.exit(1)


@notebook.command()
@option("--id", required=True, help=des_notebook)
def get(id: str):
    """Get a notebook."""
    try:
        ep = f"{notebook_ep}/{id}"
        r = request("GET", ep, True)
        check_response(r)

        d = r.json()
        res = d.get("result")

        if res is None:
            raise Exception("Data not received.")

        # Notebook data
        _id = res["id"]
        name = res["name"]
        tag_colors = res.get("tag_colors")
        created = res["created"].replace("T", " ")
        last_mod = res["last_modified"].replace("T", " ")

        if tag_colors is not None:
            tag_colors = [f"{i}={v}" for i, v in tag_colors.items()]
            tag_colors = ", ".join(tag_colors)

        echo("\nID:" + (" " * 12) + _id)
        echo(f"Name:" + (" " * 10) + name)

        if tag_colors is not None:
            echo(f"Tag colors:" + (" " * 4) + tag_colors)

        echo("Created:" + (" " * 7) + created)
        echo(f"Last modified: {last_mod}\n")
    except Exception as e:
        echo(f"Error: {e}")
        sys.exit(1)


def put_notebook(method: str, endpoint: str, name: str, tag_colors: str):
    """Put (create or update) a notebook.

    :param method: Request method ("POST" or "PUT").
    :param endpoint: Request endpoint.
    :param name: Name.
    :param tag_colors: Tag colors. E.g. "tag1=color1, tag2=color2".
    """
    data = {"name": name}
    _tag_colors = {}

    try:
        if tag_colors != "":
            col = tag_colors.replace(" ", "")
            col = tag_colors.split(",")

            for c in col:
                tag, color = c.split("=")
                _tag_colors[tag] = color

    except Exception as e:
        echo(f'Error: "tag_colors" is invalid.')
        sys.exit(1)

    if len(_tag_colors) > 0:
        data["tag_colors"] = _tag_colors

    try:
        r = request(method, endpoint, True, data)
        check_response(r)

        m = r.json().get("message")

        if m is not None:
            echo(m)
    except Exception as e:
        echo(f"Error: {e}")
        sys.exit(1)


@notebook.command()
@option("--name", prompt=True, help=des_name)
@option("--tagcolors", default="", prompt=True, help=des_tag_colors)
def create(name: str, tagcolors: str):
    """Create a notebook."""
    put_notebook("POST", notebook_ep, name, tagcolors)


@notebook.command()
@option("--id", prompt=True, help=des_notebook)
@option("--name", prompt=True, help=des_name)
@option("--tagcolors", default="", prompt=True, help=des_tag_colors)
def update(id: str, name: str, tagcolors: str):
    """Update a notebook."""
    ep = f"{notebook_ep}/{id}"
    put_notebook("PUT", ep, name, tagcolors)


@notebook.command()
@option("--id", required=True, help=des_notebook)
@confirmation_option(prompt=del_confirm)
def delete(id: str):
    """Delete a notebook."""
    try:
        ep = f"{notebook_ep}/{id}"
        r = request("DELETE", ep, True)
        check_response(r)

        m = r.json().get("message")

        if m is not None:
            echo(m)
    except Exception as e:
        echo(f"Error: {e}")
        sys.exit(1)
