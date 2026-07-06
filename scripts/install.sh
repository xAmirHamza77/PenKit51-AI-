#!/usr/bin/env bash
# Optional deployment script — copies penkit51 AI assets into a compatible platform directory.
# Usage: PLATFORM_DIR=/path/to/platform # optional: ./scripts/install.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORGE_DIR="$(dirname "$SCRIPT_DIR")"
PLATFORM_DIR="${PLATFORM_DIR:-}"

if [[ -z "$PLATFORM_DIR" || ! -d "$PLATFORM_DIR" ]]; then
  echo "penkit51 AI is self-contained. No installation required."
  echo ""
  echo "To deploy into a compatible platform runtime, set PLATFORM_DIR:"
  echo "  PLATFORM_DIR=/path/to/platform # optional: ./scripts/install.sh"
  exit 0
fi

echo "=== penkit51 AI Deployment ==="
echo "Target platform: $PLATFORM_DIR"
echo ""

BACKUP_DIR="$FORGE_DIR/.backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
[[ -d "$PLATFORM_DIR/skills" ]] && cp -R "$PLATFORM_DIR/skills" "$BACKUP_DIR/"
[[ -d "$PLATFORM_DIR/agents" ]] && cp -R "$PLATFORM_DIR/agents" "$BACKUP_DIR/"
echo "Backup saved to: $BACKUP_DIR"

python3 "$SCRIPT_DIR/merge_skills.py"
python3 "$SCRIPT_DIR/sanitize_names.py"

rsync -a --delete "$FORGE_DIR/skills/" "$PLATFORM_DIR/skills/"
for agent in "$FORGE_DIR/agents/"*.md; do
  cp "$agent" "$PLATFORM_DIR/agents/"
done
cp "$FORGE_DIR/roles/penkit51-ai.yaml" "$PLATFORM_DIR/roles/"

echo ""
echo "Deployment complete."
echo "Skills deployed: $(find "$PLATFORM_DIR/skills" -name SKILL.md | wc -l | tr -d ' ')"