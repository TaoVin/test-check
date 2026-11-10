#!/usr/bin/env bash
# 本地打包，等价于 CI 里跑的那一步。
set -euo pipefail
cd "$(dirname "$0")"
.venv/bin/python package.py "$@"
