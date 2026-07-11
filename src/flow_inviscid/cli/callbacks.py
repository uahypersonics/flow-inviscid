"""Callbacks for global CLI options in flow-inviscid."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
import logging

import typer


# --------------------------------------------------
# version callback
# --------------------------------------------------
def version_callback(value: bool) -> None:
    """Print version and exit when --version is passed."""
    if value:
        # note: __version__ is defined in flow_inviscid/__init__.py
        from flow_inviscid import __version__
        typer.echo(f"flow-inviscid {__version__}")
        raise typer.Exit()

# --------------------------------------------------
# verbose callback
# --------------------------------------------------
def verbose_callback(value: bool) -> None:
    """Enable INFO-level logging to stderr when --verbose is passed."""
    if value:
        logger = logging.getLogger("flow_inviscid")
        logger.setLevel(logging.INFO)

        # attach a stderr handler; guard prevents duplicates on repeated calls
        has_stream_handler = any(
            isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
            for h in logger.handlers
        )
        if not has_stream_handler:
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            handler.setFormatter(logging.Formatter("[%(levelname)-7s] %(name)s: %(message)s"))
            logger.addHandler(handler)


