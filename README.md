# flow-inviscid

Computes inviscid surface Mach number, pressure, and temperature along a body
contour using classical methods such as tangent-cone, tangent-wedge, Modified
Newtonian, shock-expansion, method of characteristics, and linearized supersonic.     

[![PyPI](https://img.shields.io/pypi/v/flow-inviscid)](https://pypi.org/project/flow-inviscid/)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-%E2%89%A53.11-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Install

```bash
pip install flow-inviscid
```

## Quick Start

under construction

## Documentation

## Validation and Verification

under construction

## Code Style

This project follows established Python community conventions so that
contributors can focus on the physics rather than inventing formatting rules.

| Convention | What it covers | Reference |
|---|---|---|
| [PEP 8](https://peps.python.org/pep-0008/) | Code formatting, naming, whitespace | Python standard style guide |
| [PEP 257](https://peps.python.org/pep-0257/) | Docstring structure | Python standard docstring conventions |
| [numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html) | Docstring sections (`Parameters`, `Returns`, `Attributes`) | NumPy/SciPy docstring standard |
| [Ruff](https://docs.astral.sh/ruff/) | Automated linting and formatting | Enforces PEP 8 compliance automatically |

## Releasing

This project uses [Semantic Versioning](https://semver.org/) (`vMAJOR.MINOR.PATCH`):

- **MAJOR** (`v1.0.0`): Breaking API changes
- **MINOR** (`v0.3.0`): New features, backward-compatible
- **PATCH** (`v0.3.1`): Bug fixes

To publish a new version:

1. Verify locally:
   ```bash
   ruff check .
   pytest
   ```
2. Commit and push to `main`
3. Tag and push:
   ```bash
   git tag -a vMAJOR.MINOR.PATCH -m "Release vMAJOR.MINOR.PATCH"
   git push origin vMAJOR.MINOR.PATCH
   ```

## Citation

