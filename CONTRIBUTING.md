# Contributing to flow-inviscid

Contributions are welcome, whether in the form of bug fixes, documentation
improvements, or new physics implementations.

## Setting Up a Development Environment

Clone the repository and install in editable mode with all development
dependencies:

```bash
git clone https://github.com/uahypersonics/flow-inviscid.git
cd flow-inviscid
pip install -e ".[dev]"
```

## Running the Tests

```bash
pytest
```

All tests must pass before submitting a pull request.

## Code Style

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and
formatting.  Run it before committing:

```bash
ruff check .
ruff format .
```

The CI pipeline runs both checks automatically.  See the code style table in
[README.md](README.md) for the full conventions (PEP 8, PEP 257, numpydoc).

## Contributing Physics or Equations

Changes that touch governing equations, transformations, or numerical methods
should:

- Reference the relevant literature in the docstring (author, year, equation
  number)
- Include a test or validation case that demonstrates correctness against a known
  result

If a proposed change may be inconsistent with the formulation, open an issue
first to discuss before writing code.

## Reporting Bugs

Open an issue on GitHub with:

- A minimal reproducible example
- The `flow-inviscid` version (`pip show flow-inviscid`)
- Python version and operating system
- Expected vs. actual behavior

## License

All contributions are made under the [BSD-3-Clause License](LICENSE).
