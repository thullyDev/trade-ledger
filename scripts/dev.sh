#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r backend/requirements.txt

python backend/seed.py

if [[ ! -d frontend/node_modules ]]; then
  npm install --prefix frontend --silent
fi

trap 'kill $(jobs -p) 2>/dev/null || true' EXIT
(
  cd backend
  export PYTHONPATH=.
  exec uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
) &
(
  cd frontend
  exec npm run dev
) &
wait