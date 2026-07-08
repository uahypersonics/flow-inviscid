"""CLI handler for ``flow-inviscid tangent-cone``."""

from __future__ import annotations

import typer


def cmd_tangent_cone() -> None:
    """Tangent-cone surface conditions (not yet implemented)."""
    typer.echo("Not implemented yet.", err=True)
    raise typer.Exit(1)

