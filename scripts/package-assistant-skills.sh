#!/usr/bin/env bash
# Package assistant skills for manual installation (no auto-deploy)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORGE_DIR="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$FORGE_DIR/dist"
ASST_DIR="$FORGE_DIR/assistant-skills"

mkdir -p "$DIST_DIR"

echo "=== Packaging penkit51 Assistant Skills ==="

# ChatGPT upload zip (Agent Skills standard folder)
CHATGPT_SRC="$ASST_DIR/chatgpt/penkit51-ai"
CHATGPT_ZIP="$DIST_DIR/penkit51-ai-chatgpt.zip"
rm -f "$CHATGPT_ZIP"
(cd "$CHATGPT_SRC" && zip -r "$CHATGPT_ZIP" .)
echo "ChatGPT:  $CHATGPT_ZIP"

# Claude zip (optional manual upload)
CLAUDE_SRC="$ASST_DIR/claude/penkit51-ai"
CLAUDE_ZIP="$DIST_DIR/penkit51-ai-claude.zip"
rm -f "$CLAUDE_ZIP"
(cd "$CLAUDE_SRC" && zip -r "$CLAUDE_ZIP" .)
echo "Claude:    $CLAUDE_ZIP"

# Grok zip
GROK_SRC="$ASST_DIR/grok/penkit51-ai"
GROK_ZIP="$DIST_DIR/penkit51-ai-grok.zip"
rm -f "$GROK_ZIP"
(cd "$GROK_SRC" && zip -r "$GROK_ZIP" .)
echo "Grok:      $GROK_ZIP"

echo ""
echo "Upload ChatGPT zip at: https://chatgpt.com/skills → New skill → Upload"
echo "Install Claude skill:  cp -R assistant-skills/claude/penkit51-ai ~/.claude/skills/"
echo "Install Grok skill:    cp -R assistant-skills/grok/penkit51-ai ~/.grok/skills/"