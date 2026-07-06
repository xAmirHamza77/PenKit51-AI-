#!/usr/bin/env bash
# Install penkit51 assistant skills to local assistant directories (manual opt-in)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORGE_DIR="$(dirname "$SCRIPT_DIR")"
ASST_DIR="$FORGE_DIR/assistant-skills"

install_one() {
  local platform="$1"
  local src="$ASST_DIR/$platform/penkit51-ai"
  local dest="$2"

  if [[ ! -d "$src" ]]; then
    echo "SKIP $platform: source not found"
    return 1
  fi

  mkdir -p "$(dirname "$dest")"
  rm -rf "$dest"
  cp -R "$src" "$dest"
  echo "Installed $platform → $dest"
}

echo "=== penkit51 Assistant Skill Installer ==="
echo ""

case "${1:-all}" in
  claude)
    install_one claude "$HOME/.claude/skills/penkit51-ai"
    ;;
  chatgpt)
    "$SCRIPT_DIR/package-assistant-skills.sh"
    echo ""
    echo "ChatGPT requires manual upload of dist/penkit51-ai-chatgpt.zip"
    echo "Go to: https://chatgpt.com/skills → New skill → Upload from your computer"
    ;;
  grok)
    install_one grok "$HOME/.grok/skills/penkit51-ai"
    ;;
  all)
    install_one claude "$HOME/.claude/skills/penkit51-ai"
    install_one grok "$HOME/.grok/skills/penkit51-ai"
    "$SCRIPT_DIR/package-assistant-skills.sh"
    echo ""
    echo "ChatGPT: upload dist/penkit51-ai-chatgpt.zip manually at chatgpt.com/skills"
    ;;
  *)
    echo "Usage: $0 [claude|chatgpt|grok|all]"
    exit 1
    ;;
esac

echo ""
echo "Done. Invoke with: /penkit51-ai scan https://target.com"