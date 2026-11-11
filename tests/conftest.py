"""Shared pytest hooks for Nova-Commands.

Fail fast with an actionable message when the active interpreter lacks
project test deps — do not install into system Python; use a venv +
requirements-dev.txt (see README / CONTRIBUTING).
"""

from __future__ import annotations

import sys


def pytest_configure(config) -> None:  # noqa: ANN001 — pytest hook signature
    missing: list[str] = []
    for mod in ("jsonschema", "referencing", "yaml", "pytest"):
        try:
            __import__(mod if mod != "yaml" else "yaml")
        except ImportError:
            missing.append("PyYAML" if mod == "yaml" else mod)
    if missing:
        exe = sys.executable
        raise SystemExit(
            f"Missing test/validation deps for interpreter {exe}: "
            f"{', '.join(missing)}.\n"
            "Do not install into system Python. Create a project venv and install "
            "requirements-dev.txt, then re-run pytest with that interpreter:\n"
            "  python3 -m venv .venv\n"
            "  source .venv/bin/activate   # Windows: .venv\\Scripts\\activate\n"
            "  python -m pip install -r requirements-dev.txt\n"
            "  python -m pytest tests/"
        )
