#!/bin/zsh
# One-click local launcher for the HEP Graph professor demo.
set -u

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"

usable_python() {
  "$1" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1
}

PYTHON=""
for candidate in \
  "$SCRIPT_DIR/.venv/bin/python" \
  "$SCRIPT_DIR/.venv/bin/python3" \
  /opt/homebrew/bin/python3 \
  /usr/local/bin/python3 \
  "$(command -v python3 2>/dev/null || true)"; do
  if [[ -n "$candidate" && -x "$candidate" ]] && usable_python "$candidate"; then
    PYTHON="$candidate"
    break
  fi
done

if [[ -z "$PYTHON" ]]; then
  print -u2 "HEP Graph needs Python 3.11 or newer. Install it or create .venv in this project, then run Start HEP Graph.command again."
  read -r "REPLY?Press Return to close..."
  exit 1
fi

cd -- "$SCRIPT_DIR" || exit 1
exec "$PYTHON" "$SCRIPT_DIR/launch_demo.py" "$@"
