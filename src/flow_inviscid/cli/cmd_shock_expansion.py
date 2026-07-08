"""CLI handler for ``flow-inviscid shock-expansion``."""

from __future__ import annotations

import typer


def cmd_shock_expansion() -> None:
    """Shock-expansion surface conditions (not yet implemented)."""
    typer.echo("Not implemented yet.", err=True)
    raise typer.Exit(1)

