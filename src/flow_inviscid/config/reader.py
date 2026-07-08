"""Read and validate a flow-inviscid TOML config file."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import tomllib
from pathlib import Path

from flow_inviscid.config.schema import Config


# --------------------------------------------------
# read_config
# --------------------------------------------------
def read_config(path: Path) -> Config:
    """Read a TOML config file and return a validated Config.

    Args:
        path: Path to a TOML file.

    Returns:
        Validated Config dataclass.

    Raises:
        FileNotFoundError: If the config file does not exist.
        ValueError: If required sections or fields are missing or invalid.
    """

    # validate the file exists
    if not path.exists():
        raise FileNotFoundError(f"config file not found: {path}")

    # read TOML (tomllib is stdlib in Python 3.11+, which is the minimum requirement)
    with open(path, "rb") as f:
        raw = tomllib.load(f)

    # build and validate the Config struct
    return Config.from_dict(raw)
