"""CLI handler for ``flow-inviscid solve``."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import Annotated

import numpy as np
import typer

from flow_inviscid.config import read_config
from flow_inviscid.io import write_tecplot
from flow_inviscid.methods.newtonian import solve_newtonian


# --------------------------------------------------
# internal helpers
# --------------------------------------------------
def _resolve_config(name: str | None) -> Path:
    """Resolve the config file path from an optional name argument.

    Resolution rules:
      1. No argument   → scan CWD for *.toml; use it if exactly one is found.
      2. Name given    → try the name as-is; if no file found, append .toml.

    Args:
        name: optional name or path supplied by the user

    Returns:
        Resolved Path to the config file

    Raises:
        typer.Exit: if the file cannot be found or the CWD has multiple TOMLs
    """
    if name is None:
        # auto-detect: look for a single TOML in the current directory
        candidates = list(Path.cwd().glob("*.toml"))
        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) == 0:
            typer.echo("error: no .toml config file found in the current directory.", err=True)
            typer.echo("  Run `flow-inviscid init <method>` to create one.", err=True)
            raise typer.Exit(1)
        # more than one TOML — ask the user to be explicit
        names = ", ".join(p.name for p in sorted(candidates))
        typer.echo(
            f"error: multiple .toml files found ({names}). "
            "Specify which one: flow-inviscid solve <name>",
            err=True,
        )
        raise typer.Exit(1)

    # try the name as provided
    path = Path(name)
    if path.exists():
        return path

    # try appending .toml if no suffix given
    with_ext = path.with_suffix(".toml")
    if with_ext.exists():
        return with_ext

    typer.echo(f"error: config file not found: {name} (also tried {with_ext})", err=True)
    raise typer.Exit(1)


def _run_newtonian(cfg, config_path: Path) -> None:
    """Run Modified Newtonian and write Tecplot output.

    Args:
        cfg:         validated Config object
        config_path: path to the TOML file (used for error context)
    """
    # validate that required sections are present
    if cfg.flow_conditions is None or cfg.body is None or cfg.output is None:
        typer.echo(
            "error: newtonian requires [flow_conditions], [body], and [output] sections.\n"
            "  Run `flow-inviscid init newtonian` to regenerate the template.",
            err=True,
        )
        raise typer.Exit(1)

    # run the Modified Newtonian solver
    typer.echo(f"Running Modified Newtonian  (Mach from {cfg.flow_conditions.file.name})")
    result = solve_newtonian(cfg)

    # report cp_max
    typer.echo(f"  cp_max = {result.cp_max:.4f}  (M={result.mach_inf}, gamma={result.gamma})")

    # write Tecplot output
    out_path: Path = cfg.output.file
    write_tecplot(
        path=out_path,
        title=f"flow-inviscid: Modified Newtonian  M={result.mach_inf}",
        variables=["x", "y", "s", "theta_deg", "cp", "p_p_inf", "mach_surface"],
        data=[
            result.x,
            result.y,
            result.s,
            np.degrees(result.theta),
            result.cp,
            result.p_p_inf,
            result.mach,
        ],
    )
    typer.echo(f"  Written: {out_path}  ({len(result.x)} points)")


# --------------------------------------------------
# solve command
# --------------------------------------------------
def cmd_solve(
    config: Annotated[
        str | None,
        typer.Argument(
            help=(
                "Config file name or path (with or without .toml). "
                "If omitted, the single .toml in the current directory is used."
            ),
        ),
    ] = None,
) -> None:
    """Run a solve from a TOML config file.

    Reads the config, validates it, dispatches to the method under [method] name,
    and writes output as specified in [output].
    """
    # resolve which config file to use
    config_path = _resolve_config(config)

    # read and validate the TOML
    try:
        cfg = read_config(config_path)
    except (FileNotFoundError, ValueError) as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1)

    # dispatch to the correct method
    if cfg.method.name == "newtonian":
        _run_newtonian(cfg, config_path)
    else:
        typer.echo(f"error: method '{cfg.method.name}' is not yet implemented.", err=True)
        raise typer.Exit(1)

