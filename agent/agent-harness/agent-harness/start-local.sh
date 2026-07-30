#!/usr/bin/env bash
set -euo pipefail

app_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$app_dir"

if [[ ! -x .venv/bin/python ]]; then
  echo "Missing .venv. Run: uv venv && uv pip install --python .venv/bin/python -r requirements.txt" >&2
  exit 1
fi

if ! .venv/bin/python -c 'import fitz, pypdf' >/dev/null 2>&1; then
  echo "Missing PDF extraction dependencies. Run: uv pip install --python .venv/bin/python -r requirements.txt" >&2
  exit 1
fi

if [[ ! -f .poe-code-cli/launcher.mjs || ! -f .poe-code-cli/.runtime/node_modules/poe-code/dist/bin.cjs ]]; then
  echo "Missing Poe-Code-CLI installation. Extract Poe-Code-CLI.zip and run its install command first." >&2
  exit 1
fi

if ! command -v node.exe >/dev/null 2>&1 && ! command -v node >/dev/null 2>&1; then
  echo "Missing Node.js; Poe-Code-CLI requires Node.js 18.18 or newer." >&2
  exit 1
fi

frontend_stale=false
if [[ ! -f frontend/dist/index.html ]]; then
  frontend_stale=true
elif find frontend/src frontend/index.html frontend/package.json -type f -newer frontend/dist/index.html -print -quit | grep -q .; then
  frontend_stale=true
fi

if [[ "$frontend_stale" == true ]]; then
  echo "Building frontend..."
  # This repository is commonly launched from WSL while its frontend
  # dependencies were installed by Windows npm. Rollup's optional native
  # package is platform-specific, so Linux node cannot load a Windows
  # node_modules tree. Reuse Windows npm in that case instead of asking the
  # user to delete/reinstall dependencies every time the server starts.
  if [[ -d frontend/node_modules/@rollup/rollup-win32-x64-msvc ]] \
      && command -v cmd.exe >/dev/null 2>&1 \
      && command -v wslpath >/dev/null 2>&1; then
    win_frontend="$(wslpath -w "$app_dir/frontend")"
    cmd.exe /d /c "cd /d \"$win_frontend\" && npm.cmd run build"
  else
    (cd frontend && npm run build)
  fi
fi

exec .venv/bin/python main.py
