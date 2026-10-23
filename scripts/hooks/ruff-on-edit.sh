#!/usr/bin/env bash
# Claude Code PostToolUse hook: format and lint every Python file the agent edits.
set -euo pipefail

file=$(python3 -c 'import json, sys; print(json.load(sys.stdin).get("tool_input", {}).get("file_path", ""))')
[[ "$file" == *.py ]] || exit 0

ruff="${CLAUDE_PROJECT_DIR:-.}/.venv/bin/ruff"
[ -x "$ruff" ] || ruff=ruff

"$ruff" format --quiet "$file"
if ! "$ruff" check --fix --quiet "$file"; then
  echo "ruff found issues in $file that need a manual fix" >&2
  exit 2
fi
