"""flow-inviscid: inviscid supersonic and hypersonic surface solutions.

Stub release v0.1.0 -- no modules implemented yet.
"""

# --------------------------------------------------
# load version
# --------------------------------------------------
from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("flow-inviscid")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["__version__"]
