#!/usr/bin/env bash
set -euo pipefail

# $1 は Codex から渡される JSON（現状は使わなくてOK）
SOUND="${CODEX_DONE_SOUND:-$HOME/.codex/sounds/done.wav}"

if command -v paplay >/dev/null 2>&1; then
  paplay "$SOUND" >/dev/null 2>&1 || printf '\a' || true
else
  printf '\a' || true
fi

exit 0
