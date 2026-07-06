#!/usr/bin/env bash
# Rename PentestForge-AI → penkit51 AI
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PARENT="$(dirname "$ROOT")"

echo "=== Renaming project to penkit51 AI ==="

# Rename assistant skill directories
for platform in claude chatgpt grok; do
  src="$ROOT/assistant-skills/$platform/pentest-forge"
  dst="$ROOT/assistant-skills/$platform/penkit51-ai"
  if [[ -d "$src" ]]; then
    mv "$src" "$dst"
    echo "Moved $platform skill dir"
  fi
done

# Rename role file
if [[ -f "$ROOT/roles/pentest-forge.yaml" ]]; then
  mv "$ROOT/roles/pentest-forge.yaml" "$ROOT/roles/penkit51-ai.yaml"
fi

# Bulk text replacement in project files
replace_in_files() {
  local files
  files=$(find "$ROOT" \
    -type f \
    \( -name '*.md' -o -name '*.yaml' -o -name '*.py' -o -name '*.sh' -o -name '*.txt' -o -name '*.yml' \) \
    ! -path '*/.backup-*/*' \
    ! -path '*/dist/*' \
    ! -path '*/scripts/rename-to-penkit51.sh')

  while IFS= read -r file; do
    [[ -f "$file" ]] || continue
    perl -pi -e '
      s/PentestForge-AI/penkit51 AI/g;
      s/PentestForge AI/penkit51 AI/g;
      s/PentestForge/penkit51/g;
      s/pentest-forge/penkit51-ai/g;
      s/pentestforge/penkit51/g;
      s/PENTESTFORGE_/PENKIT51_/g;
      s/pentestforge-orchestrator/penkit51-orchestrator/g;
      s/pentestforge-source-aware/penkit51-source-aware/g;
      s/pfPolluted/pk51Polluted/g;
    ' "$file"
  done <<< "$files"
}

replace_in_files

# Clean old dist zips
rm -f "$ROOT/dist/"*.zip 2>/dev/null || true

# Rename root project directory
NEW_ROOT="$PARENT/penkit51-AI"
if [[ "$ROOT" != "$NEW_ROOT" ]]; then
  mv "$ROOT" "$NEW_ROOT"
  echo "Renamed project directory → $NEW_ROOT"
  ROOT="$NEW_ROOT"
fi

# Copy logo if generated in session
SESSION_LOGO="/Users/amirhamza/.grok/sessions/%2FUsers%2Famirhamza/019f375c-3ea8-74e2-8ff0-d6a297f9d7f7/images/1.jpg"
if [[ -f "$SESSION_LOGO" ]]; then
  mkdir -p "$ROOT/assets"
  cp "$SESSION_LOGO" "$ROOT/assets/logo.png"
  echo "Copied logo → assets/logo.png"
fi

echo ""
echo "Done. Project is now penkit51 AI at: $ROOT"