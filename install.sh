#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON_BIN=${PYTHON_BIN:-python3}

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python 3.10 or later is required. Install Python, then run this script again." >&2
  exit 1
fi

if [ ! -d "$ROOT_DIR/.venv" ]; then
  "$PYTHON_BIN" -m venv "$ROOT_DIR/.venv"
fi

"$ROOT_DIR/.venv/bin/python" -m pip install --upgrade pip
"$ROOT_DIR/.venv/bin/python" -m pip install -r "$ROOT_DIR/requirements.txt"

echo
echo "SiteSentry is installed. Start it with:"
echo "  $ROOT_DIR/.venv/bin/python $ROOT_DIR/backend/app.py"
echo "Then open http://127.0.0.1:5123 in your browser."
