#!/usr/bin/env bash
# Create a Python virtualenv and install project dependencies.
# Run from project root: ./scripts/setup_env.sh
# Then activate: source .venv/bin/activate (Linux/macOS) or .venv\Scripts\activate (Windows)

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

VENV_DIR="${VENV_DIR:-.venv}"
REQUIREMENTS="${REQUIREMENTS:-requirements.txt}"

if [[ ! -f "$REQUIREMENTS" ]]; then
  echo "Error: $REQUIREMENTS not found in $REPO_ROOT"
  exit 1
fi

# Prefer python3; fall back to python (common on macOS with python.org installer)
if command -v python3 &>/dev/null; then
  PYTHON=python3
elif command -v python &>/dev/null; then
  PYTHON=python
else
  echo "Error: python3 or python not found in PATH"
  exit 1
fi

echo "Creating virtualenv at $REPO_ROOT/$VENV_DIR ..."
"$PYTHON" -m venv "$VENV_DIR"

echo "Upgrading pip..."
"$VENV_DIR/bin/pip" install --upgrade pip

echo "Installing dependencies from $REQUIREMENTS ..."
"$VENV_DIR/bin/pip" install -r "$REQUIREMENTS"

echo ""
echo "Done. Activate the environment with:"
echo "  source $VENV_DIR/bin/activate   # Linux/macOS"
echo "  $VENV_DIR\\Scripts\\activate     # Windows (Cmd)"
echo ""
echo "Then copy .env.example to .env (if present), set your DB credentials, and run:"
echo "  python manage.py migrate"
echo "  python manage.py runserver"
