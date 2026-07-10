"""Extract body surface coordinates from ASCII or Tecplot geometry files.

Wraps read_ascii and returns (x, y) arrays, resolved by column name when
the header contains a VARIABLES declaration, or by position (columns 0, 1)
as a fallback.
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path

import numpy as np

from flow_inviscid.io.read_ascii import AsciiData, read_ascii


# --------------------------------------------------
# surface coordinate reader
# --------------------------------------------------
def read_surface_coordinates(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Read surface (x, y) coordinates from an ASCII or Tecplot geometry file.

    Column resolution order:
      1. Match column names "x" and "y" from the file header (case-insensitive).
      2. Fall back to columns 0 and 1 if no named columns are found.

    Args:
        path: path to the geometry file

    Returns:
        Tuple (x, y) of 1-D numpy arrays [m]

    Raises:
        ValueError: if the file has fewer than two data columns
    """
    # read the file — returns data array and any column names found in the header
    result: AsciiData = read_ascii(path)

    # validate that at least two columns are present
    if result.data.ndim != 2 or result.data.shape[1] < 2:
        raise ValueError(
            f"geometry file must have at least two columns (x  y): {path}"
        )

    # resolve x and y column indices
    names_lower = [n.lower() for n in result.column_names]
    if "x" in names_lower and "y" in names_lower:
        # match by name from VARIABLES declaration
        ix = names_lower.index("x")
        iy = names_lower.index("y")
    else:
        # fall back to first two columns
        ix, iy = 0, 1

    # extract x and y
    x = result.data[:, ix]
    y = result.data[:, iy]
    return x, y

