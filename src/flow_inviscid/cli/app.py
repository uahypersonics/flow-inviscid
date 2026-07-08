"""Typer application for the flow-inviscid command-line interface."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import logging
import sys
from typing import Annotated

import typer

# --------------------------------------------------
# package imports
# --------------------------------------------------
from flow_inviscid.cli.cmd_init import (
    cmd_init_newtonian,
    cmd_init_shock_expansion,
    cmd_init_tangent_cone,
)
from flow_inviscid.cli.cmd_solve import cmd_solve

# --------------------------------------------------
# preserve command registration order in --help output
# --------------------------------------------------

# typer adds cli.command() registrations before add_typer() groups internally,
# so self.commands would put "solve" before "init" regardless of source order.
# _COMMAND_ORDER defines the desired display order explicitly.
_COMMAND_ORDER = ["init", "solve"]

class _OrderedGroup(typer.core.TyperGroup):
    def list_commands(self, ctx: typer.Context) -> list[str]:
        # return commands in _COMMAND_ORDER first, then any unlisted ones
        ordered = [c for c in _COMMAND_ORDER if c in self.commands]
        remainder = [c for c in self.commands if c not in _COMMAND_ORDER]
        return ordered + remainder

# --------------------------------------------------
# set up typer apps
# --------------------------------------------------
cli = typer.Typer(
    name="flow-inviscid",
    help="flow-inviscid: inviscid surface conditions for supersonic and hypersonic bodies",
    no_args_is_help=True,
    add_completion=False,
    cls=_OrderedGroup,
)

# --------------------------------------------------
# init subgroup: generates a config file for a given method
# --------------------------------------------------
init_app = typer.Typer(
    name="init",
    help="Generate a config file for a surface-condition method.",
    no_args_is_help=True,
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

    # store verbose flag in context for subcommands
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

# init subgroup with one subcommand per method -- registered first so it appears first in --help
cli.add_typer(init_app, name="init")
# register init subcommands for each method
# call cmd_init_* functions to generate a config file for each method (note: method has to be registered in config/schema.py as a valid method name)
init_app.command(name="tangent-cone"   )(cmd_init_tangent_cone)
init_app.command(name="newtonian"      )(cmd_init_newtonian)
init_app.command(name="shock-expansion")(cmd_init_shock_expansion)

# solve: reads a config file and dispatches on [method] -- registered after init
cli.command(name="solve", no_args_is_help=True)(cmd_solve)


# --------------------------------------------------
# entry point
# --------------------------------------------------
if __name__ == "__main__":
    cli()
