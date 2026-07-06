#!/usr/bin/env bash
# One-time setup: populate neutral upstream skill directories for merge_skills.py
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORGE_DIR="$(dirname "$SCRIPT_DIR")"
PARENT_DIR="$(dirname "$FORGE_DIR")"

EXPLOIT_SRC="${PENKIT51_EXPLOITATION_SRC:-}"
PLATFORM_SRC="${PENKIT51_PLATFORM_SRC:-}"

if [[ -z "$EXPLOIT_SRC" ]]; then
  while IFS= read -r -d '' candidate; do
    if [[ -f "$candidate/vulnerabilities/sql_injection.md" ]]; then
      EXPLOIT_SRC="$candidate"
      break
    fi
  done < <(find "$PARENT_DIR" -type d -name skills -print0 2>/dev/null)
fi

if [[ -z "$PLATFORM_SRC" ]]; then
  for candidate in "$PARENT_DIR"/*/skills; do
    if [[ -d "$candidate" && -f "$candidate/sql-injection-testing/SKILL.md" ]]; then
      PLATFORM_SRC="$candidate"
      break
    fi
  done
fi

if [[ -z "$EXPLOIT_SRC" || ! -d "$EXPLOIT_SRC" ]]; then
  echo "ERROR: exploitation skill source not found."
  echo "Set PENKIT51_EXPLOITATION_SRC=/path/to/exploitation/skills"
  exit 1
fi

if [[ -z "$PLATFORM_SRC" || ! -d "$PLATFORM_SRC" ]]; then
  echo "ERROR: platform skill source not found."
  echo "Set PENKIT51_PLATFORM_SRC=/path/to/platform/skills"
  exit 1
fi

mkdir -p "$FORGE_DIR/upstream"
rsync -a --delete "$EXPLOIT_SRC/" "$FORGE_DIR/upstream/exploitation-skills/"
rsync -a --delete "$PLATFORM_SRC/" "$FORGE_DIR/upstream/platform-skills/"

echo "Upstream sources prepared under $FORGE_DIR/upstream/"