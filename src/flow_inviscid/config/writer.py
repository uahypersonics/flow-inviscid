"""Write a flow-inviscid TOML config file from a template."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path

import typer

from flow_inviscid.config.template import TEMPLATES


# --------------------------------------------------
# write_config
# --------------------------------------------------
def write_config(method_key: str, path: Path, force: bool = False) -> None:
    """Write a TOML config file for the given method.

    Args:
        method_key: Internal method key (e.g. "tangent_cone").
                    Must be a key in config.template.TEMPLATES.
        path: Output file path.
        force: When True, overwrite an existing file without prompting.
               When False (default), exit with an error if the file exists.
    """

    # refuse to overwrite unless --force was passed
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

    # fetch content from TEMPLATES for this method (specified in template.py)
    # note: method key is automatically set based on subcommand (e.g. tangent_cone, newtonian, shock_expansion) so it will always be valid
    content = TEMPLATES[method_key]

    # write the template content for this method
    path.write_text(content)

    # report what was written and how to use it
    typer.echo(f"Written: {path}")
    typer.echo(f"Edit {path} to add body, freestream, and output settings.")
    typer.echo(f"Then run: flow-inviscid solve {path}")
