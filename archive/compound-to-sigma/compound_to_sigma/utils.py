"""Shared utilities: logging, subprocess helpers, environment expansion."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


class Logger:
    """Simple verbosity-aware logger."""

    def __init__(self, verbose: int = 1):
        self.verbose = verbose

    def debug(self, msg: str) -> None:
        if self.verbose >= 2:
            print(msg)

    def info(self, msg: str) -> None:
        if self.verbose >= 1:
            print(msg)

    def error(self, msg: str) -> None:
        print(f"ERROR: {msg}")


def expand_env_vars(value: Any) -> Any:
    """Expand environment variables in string values."""
    if isinstance(value, str):
        return os.path.expandvars(value)
    return value


def which(cmd: str) -> str | None:
    """Return the path to an executable, or None if not found."""
    return shutil.which(cmd)


def run_command(
    cmd: list[str],
    cwd: Path | str | None = None,
    verbose: int = 0,
    check: bool = True,
    capture_output: bool = True,
) -> subprocess.CompletedProcess:
    """Run a shell command, optionally streaming output at verbose >= 2."""
    if verbose >= 2:
        print(f"$ {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=check,
            text=True,
        )
        return result

    result = subprocess.run(
        cmd,
        cwd=cwd,
        check=check,
        capture_output=capture_output,
        text=True,
    )
    return result


def ensure_dir(path: Path) -> Path:
    """Create directory if it does not exist and return the path."""
    path.mkdir(parents=True, exist_ok=True)
    return path
