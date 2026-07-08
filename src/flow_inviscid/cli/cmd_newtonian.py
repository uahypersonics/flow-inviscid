"""CLI handler for ``flow-inviscid newtonian``."""

from __future__ import annotations

import typer


def cmd_newtonian() -> None:
    """Modified Newtonian surface conditions (not yet implemented)."""
    typer.echo("Not implemented yet.", err=True)
    raise typer.Exit(1)

