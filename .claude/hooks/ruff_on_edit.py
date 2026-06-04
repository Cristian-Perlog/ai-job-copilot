#!/usr/bin/env python3
"""PostToolUse hook: auto-format/lint a backend .py file after Edit/Write.

Reads the hook payload from stdin, pulls tool_input.file_path, and — only if
that file is a .py under the repo's backend/ dir — runs ruff format then
ruff check --fix on it via uv. Convenience only: always exits 0 so it can
never block a tool call, and errors are printed rather than raised.
"""

import json
import subprocess
import sys
from pathlib import Path

# Repo layout: <repo>/.claude/hooks/ruff_on_edit.py -> backend is two levels up.
BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"


def main() -> None:
    # Parse the hook JSON from stdin; bail quietly on anything malformed.
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return
    raw = (payload.get("tool_input") or {}).get("file_path")
    if not raw:
        return

    path = Path(raw).resolve()
    # Only touch Python files that live under backend/.
    if path.suffix != ".py":
        return
    try:
        path.relative_to(BACKEND_DIR)
    except ValueError:
        return

    # Format then lint-fix, both scoped via uv's --directory so the right
    # project/venv is used regardless of the hook's cwd.
    for cmd in (["ruff", "format", str(path)], ["ruff", "check", "--fix", str(path)]):
        try:
            subprocess.run(
                ["uv", "run", "--directory", str(BACKEND_DIR), *cmd],
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception as exc:  # uv missing, etc. — never fail the tool call.
            print(f"ruff_on_edit: skipped ({exc})")
            return
    print(f"ruff_on_edit: formatted {path.name}")


if __name__ == "__main__":
    main()
    sys.exit(0)  # Non-blocking: always succeed.
