# Contributing

Thanks for considering a contribution.

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

On macOS or Linux:

```bash
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quality Checks

Before opening a pull request, run:

```bash
pytest
ruff check .
```

## Pull Requests

Please keep changes focused, describe the user-facing behavior, and include tests for
logic changes when practical.
