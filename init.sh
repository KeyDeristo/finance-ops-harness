#!/usr/bin/env sh
# Thin POSIX wrapper around the cross-platform entry point.
# All logic lives in checks/init.py so Windows users without Git Bash can run
# `python checks/init.py` and both paths stay in sync.
set -eu
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
    exec python3 checks/init.py "$@"
else
    exec python checks/init.py "$@"
fi
