"""CLI handlers for ``flow-inviscid init <method>``.

Each function calls config.writer.write_config with the appropriate method key
to generate a starter TOML config file.  The template content lives in
config/template.py and grows organically as new sections are added.
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from flow_inviscid.config.writer import write_config

# --------------------------------------------------
# define shared options for init subcommands
# --------------------------------------------------

# force option: overwrite an existing file if it already exists
_FORCE_OPTION = Annotated[
    # --force is a boolean flag -> toggle, does not take a value
    bool,
    # typer.Option decorator defines the CLI option and its help text
    typer.Option("--force", "-f", help="Overwrite the output file if it already exists (default: False)."),
]


# --------------------------------------------------
# shared helper:
# - check if file exists and refuse unless --force was requested
# - write the config file
# --------------------------------------------------
def _init(method_key: str, path: Path, force: bool) -> None:
    """Check existence, write config, and report to the user."""
    # check if file exists before writing; refuse unless force was requested
    if path.exists() and not force:
        typer.echo(
            typer.style(
                f"error: {path} already exists. Use --force to overwrite.",
                fg=typer.colors.RED,
                bold=True,
            ),
            err=True,
        )
        raise typer.Exit(1)
    # write the template file
    write_config(method_key, path)
    # report what was written and how to run it
    typer.echo(f"Written: {path}")
    typer.echo(f"Edit {path} to add body, freestream, and output settings.")
    typer.echo(f"Then run: flow-inviscid solve {path}")


# --------------------------------------------------
# init tangent-cone
# --------------------------------------------------
def cmd_init_tangent_cone(
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output config file path."),
    ] = Path("tangent_cone.toml"),
    force: _FORCE_OPTION = False,
) -> None:
    """Generate a config file for the tangent-cone method."""
    _init("tangent_cone", output, force)


# --------------------------------------------------
# init newtonian
# --------------------------------------------------
def cmd_init_newtonian(
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output config file path."),
    ] = Path("newtonian.toml"),
    force: _FORCE_OPTION = False,
) -> None:
    """Generate a config file for the Modified Newtonian method."""
    _init("newtonian", output, force)


# --------------------------------------------------
# init shock-expansion
# --------------------------------------------------
def cmd_init_shock_expansion(
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output config file path."),
    ] = Path("shock_expansion.toml"),
    force: _FORCE_OPTION = False,
) -> None:
    """Generate a config file for the shock-expansion method."""
    _init("shock_expansion", output, force)
