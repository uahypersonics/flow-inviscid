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
    write_config("tangent_cone", output, force=force)


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
    write_config("newtonian", output, force=force)


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
    write_config("shock_expansion", output, force=force)
