"""Typer application for the flow-inviscid command-line interface."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import logging
import sys
from typing import Annotated

import typer

from flow_inviscid.cli.cmd_newtonian import cmd_newtonian
from flow_inviscid.cli.cmd_shock_expansion import cmd_shock_expansion

# --------------------------------------------------
# package imports
# --------------------------------------------------
from flow_inviscid.cli.cmd_tangent_cone import cmd_tangent_cone

# --------------------------------------------------
# set up typer app
# --------------------------------------------------
cli = typer.Typer(
    name="flow-inviscid",
    help="flow-inviscid: inviscid surface conditions for supersonic and hypersonic bodies",
    no_args_is_help=True,
    add_completion=False,
)


# --------------------------------------------------
# version callback
# --------------------------------------------------
def _version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        from flow_inviscid import __version__
        typer.echo(f"flow-inviscid {__version__}")
        raise typer.Exit()


# --------------------------------------------------
# main callback
# --------------------------------------------------
@cli.callback()
def main(
    ctx: typer.Context,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-V",
            help="Show version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable informational output."),
    ] = False,
) -> None:
    """flow-inviscid: inviscid surface conditions for supersonic and hypersonic bodies."""

    # store verbose flag in context for access by subcommands
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    # configure logging if verbose is requested
    if verbose:
        logger = logging.getLogger("flow_inviscid")
        logger.setLevel(logging.INFO)

        # attach a stderr handler; guard prevents duplicates
        has_stream_handler = any(
            isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
            for h in logger.handlers
        )
        if not has_stream_handler:
            handler = logging.StreamHandler(sys.stderr)
            handler.setLevel(logging.INFO)
            handler.setFormatter(logging.Formatter("[%(levelname)-7s] %(name)s: %(message)s"))
            logger.addHandler(handler)


# --------------------------------------------------
# command registration
# --------------------------------------------------
cli.command("tangent-cone",    no_args_is_help=True)(cmd_tangent_cone)
cli.command("newtonian",       no_args_is_help=True)(cmd_newtonian)
cli.command("shock-expansion", no_args_is_help=True)(cmd_shock_expansion)


# --------------------------------------------------
# entry point
# --------------------------------------------------
if __name__ == "__main__":
    cli()
