#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then python3 -m venv .venv; fi
if [ ! -f .venv/opendraft-installed ]; then
  .venv/bin/python -m pip install -e 'engine[pdf]' -r requirements.txt
  touch .venv/opendraft-installed
fi
exec .venv/bin/python codex-web/server.py "$@"
