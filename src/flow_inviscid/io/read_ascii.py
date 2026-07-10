"""Read numerical data from ASCII text files with unknown header structure
unknown number of data lines or columns.

"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import re
import warnings
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


# --------------------------------------------------
# result dataclass
# --------------------------------------------------
@dataclass
class AsciiData:
    """Result of read_ascii: numerical data plus any column names found in the header."""

    # numerical data array, shape (n_rows, n_cols)
    data: np.ndarray

    # column names extracted from the file header (e.g. Tecplot VARIABLES line)
    # empty list if the header contained no recognisable variable declarations
    column_names: list[str] = field(default_factory=list)


# --------------------------------------------------
# helper to identify data lines (can all words be parsed as floats)
# --------------------------------------------------
def _is_data_line(line: str) -> bool:
    """Return True if every word on the line parses as a finite float."""

    # split line into words using whitespace as delimiter
    words = line.split()

    # empty line is not a data line
    if not words:
        is_data = False

    else:
        # try to convert each word to a float
        try:
            values = [float(w) for w in words]
        except ValueError:
            # at least one word is not a float -> not a data line
            is_data = False
        else:
            # all words converted: except block did not fire

            # check that all values are finite (not inf or nan)
            is_data = all(np.isfinite(v) for v in values)

    # return True if the line is a data line, False otherwise
    return is_data

# --------------------------------------------------
# helper to extract variable names from header lines
# --------------------------------------------------
def _extract_variable_names(header_lines: list[str]) -> list[str]:
    """Extract column names from header lines.

    Handles the Tecplot VARIABLES declaration, which may appear on a single
    line or span multiple lines with one quoted name per line:

        VARIABLES = "x" "y" "z"        # single-line form
        VARIABLES = "x"                 # multi-line form
        "y"
        "z"

    Names are returned in declaration order, stripped of quotes.
    Returns an empty list if no VARIABLES declaration is found.

    Args:
        header_lines: raw non-numeric lines collected before the data block

    Returns:
        list of column name strings, or empty list
    """
    names: list[str] = []

    # flag: are we inside a VARIABLES block?
    in_variables = False

    for line in header_lines:
        stripped = line.strip()

        # check if this line starts a VARIABLES declaration
        if re.match(r"(?i)^variables\s*=", stripped):
            in_variables = True

        if in_variables:
            # extract all double-quoted strings from this line
            found = re.findall(r'"([^"]+)"', stripped)
            names.extend(found)

            # the VARIABLES block ends when the line contains no quoted strings
            # and is not the opening VARIABLES line itself
            if not found and not re.match(r"(?i)^variables\s*=", stripped):
                in_variables = False

    return names

# --------------------------------------------------
# public API
# --------------------------------------------------
def read_ascii(path: Path | str) -> AsciiData:
    """Read a numerical ASCII file, auto-detecting and skipping header lines.

    Args:
        path: path to the ASCII data file

    Returns:
        AsciiData with a data ndarray of shape (n_rows, n_cols) and
        a column_names list extracted from the header (may be empty)

    Raises:
        ValueError: if no numeric data rows are found
        ValueError: if rows have inconsistent column counts
    """
    # try UTF-8 first (standard); fall back to latin-1 for Fortran-generated
    # files that contain non-UTF-8 bytes in header lines
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.readlines()
    except UnicodeDecodeError:
        with open(path, encoding="latin1") as fh:
            lines = fh.readlines()

    # comment tokens recognised across common scientific file formats
    # extend this list as new formats are encountered
    _COMMENT_TOKENS = (
        "#",
        "!",
        "%",
        "$",
        "@",
        "*",
    )

    # create container for data lines (empty at the start)
    data_lines: list[list[float]] = []

    # collect header lines for variable name extraction
    header_lines: list[str] = []

    # initialize a data_started flag
    data_started = False

    # initialize the expected column count (unknown at the start)
    n_cols: int | None = None

    # loop over all lines from the raw input file
    for line in lines:

        # strip leading/trailing whitespace from the raw line
        line_stripped = line.strip()

        # skip blank lines
        if not line_stripped:
            continue

        # comment lines: collect into header while in header region, skip once data has started
        if line_stripped.startswith(_COMMENT_TOKENS):
            if not data_started:
                # strip the leading comment token and collect for variable name extraction
                header_lines.append(line_stripped.lstrip("".join(_COMMENT_TOKENS)).strip())
            continue

        if not _is_data_line(line_stripped):
            if data_started:
                # non-numeric line after data has started —> likely a zone separator
                # or a second dataset header; stop reading and warn the user
                warnings.warn(
                    f"{path}: non-numeric line encountered after data started "
                    f"('{line_stripped[:60]}'). "
                    "Only the first data block is read.",
                    UserWarning,
                    stacklevel=2,
                )
                # break out of the line in lines loop
                break
            else:
                # still in header region — collect for variable name parsing
                header_lines.append(line_stripped)
                continue

        # if we go past the if not data statement it is a data line (numeric line)

        # flip the data_started flag to True
        data_started = True

        # parse the current line into a list of floats
        row = [float(t) for t in line_stripped.split()]

        # set expected column count from first data row
        if n_cols is None:
            n_cols = len(row)

        # validate column consistency
        if len(row) != n_cols:
            raise ValueError(
                f"{path}: inconsistent column count at data row "
                f"{len(data_lines) + 1} (expected {n_cols}, got {len(row)})"
            )

        # append the parsed row to the data container
        data_lines.append(row)

    # validate that we found something
    if not data_lines:
        raise ValueError(f"{path}: no numeric data rows found")

    # extract column names from the collected header lines
    column_names = _extract_variable_names(header_lines)

    # return data array and column names
    return AsciiData(data=np.array(data_lines), column_names=column_names)
