#!/usr/bin/env python3
"""Remove legacy upstream project name references from penkit51 AI files."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REPLACEMENTS: list[tuple[str, str]] = [
    (
        "> **penkit51 AI** — merged from Strix deep exploitation techniques "
        "+ CyberStrikeAI methodology. Authorized testing only.",
        "> **penkit51 AI** — professional penetration testing skill pack. Authorized testing only.",
    ),
    ("## Deep Exploitation Guide (Strix)", "## Deep Exploitation Guide"),
    ("## Platform Methodology (CyberStrikeAI)", "## Platform Methodology"),
    ("when running inside CyberStrikeAI", "when running inside the penkit51 platform"),
    ("/workspace/.strix-source-aware", "/workspace/.penkit51-source-aware"),
    ("strixPolluted", "pk51Polluted"),
    ("There is no separate Strix Python executor.", "Use the platform shell executor for Python."),
    (
        "merges Strix deep exploitation skills with CyberStrikeAI tooling",
        "full-spectrum AI penetration testing with deep exploitation skills and integrated tooling",
    ),
    ("Combine Strix-grade deep exploitation knowledge", "Apply professional-grade deep exploitation knowledge"),
    ("## Deep Testing Principles (from Strix)", "## Deep Testing Principles"),
    ("## CyberStrikeAI Integration", "## Platform Integration"),
    ("When running inside CyberStrikeAI platform:", "When running inside the penkit51 platform:"),
    (
        "combining Strix deep exploitation knowledge with CyberStrikeAI's 100+ security tools",
        "combining deep exploitation knowledge with 100+ integrated security tools",
    ),
    (
        "Full-spectrum AI penetration testing with Strix-enhanced skills",
        "Full-spectrum AI penetration testing with enhanced exploitation skills",
    ),
    (
        "merges Strix deep methodology with CyberStrikeAI multi-agent orchestration",
        "master coordinator for multi-agent orchestration, skill loading, and evidence tracking",
    ),
    (
        "You combine Strix's deep exploitation methodology with CyberStrikeAI's multi-agent tooling",
        "You combine deep exploitation methodology with multi-agent tooling",
    ),
    ("loads Strix-enhanced skills", "loads enhanced exploitation skills"),
    ("Strix deep guides + CyberStrike methodology", "Deep exploitation guides + platform methodology"),
    ("**The best of CyberStrikeAI + Strix, unified into one AI penetration testing platform.**", "**A unified AI penetration testing platform with deep skills and full tooling.**"),
    ("penkit51 AI merges:\n- **CyberStrikeAI** — Go platform with 100+ security tools, multi-agent orchestration (Eino), MCP, web UI, C2, vulnerability management, knowledge base\n- **Strix** — 52 deep exploitation skills with PoC validation, bypass techniques, and professional pentest methodology", "penkit51 AI provides:\n- **Platform runtime** — 100+ security tools, multi-agent orchestration, MCP, web UI, vulnerability management, knowledge base\n- **Deep skills** — 63 exploitation skill packs with PoC validation, bypass techniques, and professional pentest methodology"),
    ("### 1. Install into CyberStrikeAI", "### 1. Deploy to Your Platform"),
    ("### 2. Configure CyberStrikeAI", "### 2. Configure the Platform"),
    ('Edit `CyberStrikeAI-main/config.yaml`:', "Edit your platform `config.yaml`:"),
    ("cd ../CyberStrikeAI-main", "cd /path/to/your-platform"),
    ("The `penkit51-ai` skill is auto-installed to `~/.grok/skills/penkit51-ai/`.", "Copy `grok-skills/penkit51-ai/SKILL.md` to your assistant skills directory."),
    ("│   ├── orchestrator.md  # Master coordinator (replaces default)", "│   ├── orchestrator.md  # Master coordinator"),
    ("│   └── install.sh       # Deploy into CyberStrikeAI", "│   └── install.sh       # Optional platform deployment"),
    ("1. **Strix Deep Guide**", "1. **Deep Exploitation Guide**"),
    ("2. **CyberStrike Methodology**", "2. **Platform Methodology**"),
    ("# Regenerate skills from source projects", "# Regenerate skills from upstream skill sources"),
    ("After updating source projects:", "After updating upstream skill sources:"),
    ("./scripts/install.sh", "# optional: ./scripts/install.sh"),
]


def sanitize_text(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    # Catch remaining case-insensitive standalone mentions
    text = re.sub(r"\bCyberStrikeAI\b", "the platform", text)
    text = re.sub(r"\bcyberstrike-ai\b", "penkit51", text, flags=re.IGNORECASE)
    text = re.sub(r"\bStrix\b", "penkit51", text)
    text = re.sub(r"\bstrix\b", "penkit51", text)
    return text


def main() -> None:
    targets: list[Path] = []
    for pattern in ("**/*.md", "**/*.yaml", "**/*.sh"):
        targets.extend(ROOT.glob(pattern))
    # Only sanitize merge_skills.py output strings, not path logic
    targets.append(ROOT / "scripts" / "merge_skills.py")

    changed = 0
    for path in sorted(set(targets)):
        if path.name == "sanitize_names.py":
            continue
        if path.name == "prepare_upstream.sh":
            continue
        if ".backup-" in str(path):
            continue
        original = path.read_text(encoding="utf-8")
        updated = sanitize_text(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            print(f"updated: {path.relative_to(ROOT)}")

    print(f"\nSanitized {changed} files.")


if __name__ == "__main__":
    main()