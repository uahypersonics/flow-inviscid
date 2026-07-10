"""Write flow-inviscid results to Tecplot ASCII files."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path

import numpy as np


# --------------------------------------------------
# Tecplot ASCII writer
# --------------------------------------------------
def write_tecplot(
    path: Path,
    title: str,
    variables: list[str],
    data: list[np.ndarray],
) -> None:
    """Write a single-zone ordered Tecplot ASCII (POINT format) file.

    Args:
        path:      output file path
        title:     TITLE string for the Tecplot header
        variables: list of variable name strings
        data:      list of 1-D arrays, one per variable (must all be the same length)

    Raises:
        ValueError: if data arrays have inconsistent lengths
    """
    # validate array lengths
    lengths = {len(a) for a in data}
    if len(lengths) != 1:
        raise ValueError(f"all data arrays must have the same length: got {lengths}")
    n_points = lengths.pop()

    # build variable string for the header
    var_str = " ".join(f'"{v}"' for v in variables)

    # write header and data
    with open(path, "w") as fh:
        # write Tecplot header
        fh.write(f'TITLE = "{title}"\n')
        fh.write(f"VARIABLES = {var_str}\n")
        fh.write(f'ZONE T="zone1", I={n_points}, F=POINT\n')

        # write one row per surface point
        cols = np.column_stack(data)
        for row in cols:
            fh.write("  ".join(f"{v:.8e}" for v in row) + "\n")
