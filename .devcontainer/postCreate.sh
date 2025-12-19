#!/usr/bin/env bash
set -euo pipefail

# Python 仮想環境を作成し、依存をインストール
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PATH="$REPO_ROOT/.venv"
if [ ! -d "$VENV_PATH" ]; then
  python -m venv "$VENV_PATH"
fi
# shellcheck disable=SC1091
source "$VENV_PATH/bin/activate"
python -m pip install --upgrade pip
pip install --no-cache-dir -r "$REPO_ROOT/requirements.txt"

# Codex CLI（OpenAI）をインストール（Node.js/npmが必要）
if ! command -v codex >/dev/null 2>&1; then
  npm i -g @openai/codex
fi

# --- notify用: paplay（PulseAudioクライアント）を導入 ---
if ! command -v paplay >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y --no-install-recommends pulseaudio-utils
  sudo rm -rf /var/lib/apt/lists/*
fi

# --- notify用: ~/.codex/config.toml を作成し、リポジトリ内スクリプト/音をリンク ---
mkdir -p "$HOME/.codex/sounds"
ln -sf "$(pwd)/.devcontainer/codex_notify.sh" "$HOME/.codex/notify.sh"
ln -sf "$(pwd)/.devcontainer/sounds/done.wav" "$HOME/.codex/sounds/done.wav"
chmod +x "$(pwd)/.devcontainer/codex_notify.sh" "$HOME/.codex/notify.sh"

cat > "$HOME/.codex/config.toml" <<TOML
# 1ターン完了ごとに呼ばれる。引数1にJSONペイロードが渡る。
notify = ["bash", "$HOME/.codex/notify.sh"]
TOML
