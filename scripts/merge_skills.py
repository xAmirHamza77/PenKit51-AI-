#!/usr/bin/env python3
"""Merge upstream skill sources into unified penkit51 Agent Skills format."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "skills"


def _upstream_dirs() -> tuple[Path, Path]:
    """Resolve upstream skill sources from env vars or neutral local paths."""
    exploitation = os.environ.get("PENKIT51_EXPLOITATION_SRC")
    platform = os.environ.get("PENKIT51_PLATFORM_SRC")
    if exploitation and platform:
        return Path(exploitation), Path(platform)

    local_exploit = ROOT / "upstream" / "exploitation-skills"
    local_platform = ROOT / "upstream" / "platform-skills"
    if local_exploit.is_dir() and local_platform.is_dir():
        return local_exploit, local_platform

    raise SystemExit(
        "Upstream skill sources not found.\n"
        "Run: ./scripts/prepare_upstream.sh\n"
        "Or set PENKIT51_EXPLOITATION_SRC and PENKIT51_PLATFORM_SRC"
    )

# Upstream exploitation skill path -> unified skill directory name
EXPLOITATION_MAP = {
    "vulnerabilities/sql_injection.md": "sql-injection-testing",
    "vulnerabilities/xss.md": "xss-testing",
    "vulnerabilities/ssrf.md": "ssrf-testing",
    "vulnerabilities/csrf.md": "csrf-testing",
    "vulnerabilities/xxe.md": "xxe-testing",
    "vulnerabilities/idor.md": "idor-testing",
    "vulnerabilities/business_logic.md": "business-logic-testing",
    "vulnerabilities/rce.md": "command-injection-testing",
    "vulnerabilities/insecure_deserialization.md": "deserialization-testing",
    "vulnerabilities/insecure_file_uploads.md": "file-upload-testing",
    "vulnerabilities/authentication_jwt.md": "authentication-jwt-testing",
    "vulnerabilities/nosql_injection.md": "nosql-injection-testing",
    "vulnerabilities/ssti.md": "ssti-testing",
    "vulnerabilities/prototype_pollution.md": "prototype-pollution-testing",
    "vulnerabilities/race_conditions.md": "race-conditions-testing",
    "vulnerabilities/http_request_smuggling.md": "http-request-smuggling-testing",
    "vulnerabilities/open_redirect.md": "open-redirect-testing",
    "vulnerabilities/mass_assignment.md": "mass-assignment-testing",
    "vulnerabilities/information_disclosure.md": "information-disclosure-testing",
    "vulnerabilities/subdomain_takeover.md": "subdomain-takeover-testing",
    "vulnerabilities/broken_function_level_authorization.md": "broken-function-level-authorization",
    "vulnerabilities/header_injection.md": "header-injection-testing",
    "vulnerabilities/llm_prompt_injection.md": "llm-prompt-injection-testing",
    "vulnerabilities/path_traversal_lfi_rfi.md": "path-traversal-lfi-rfi-testing",
    "protocols/graphql.md": "graphql-security-testing",
    "protocols/oauth.md": "oauth-security-testing",
    "frameworks/fastapi.md": "fastapi-security-testing",
    "frameworks/nextjs.md": "nextjs-security-testing",
    "frameworks/django.md": "django-security-testing",
    "frameworks/nestjs.md": "nestjs-security-testing",
    "technologies/supabase.md": "supabase-security-testing",
    "technologies/firebase_firestore.md": "firebase-firestore-security-testing",
    "cloud/aws.md": "aws-security-audit",
    "cloud/kubernetes.md": "kubernetes-security-testing",
    "scan_modes/deep.md": "deep-pentest-methodology",
    "scan_modes/standard.md": "standard-pentest-methodology",
    "scan_modes/quick.md": "quick-pentest-methodology",
    "coordination/root_agent.md": "pentest-orchestration",
    "coordination/source_aware_whitebox.md": "source-aware-whitebox-testing",
    "custom/source_aware_sast.md": "source-aware-sast",
    "tooling/nmap.md": "nmap-tooling",
    "tooling/nuclei.md": "nuclei-tooling",
    "tooling/httpx.md": "httpx-tooling",
    "tooling/ffuf.md": "ffuf-tooling",
    "tooling/subfinder.md": "subfinder-tooling",
    "tooling/naabu.md": "naabu-tooling",
    "tooling/katana.md": "katana-tooling",
    "tooling/sqlmap.md": "sqlmap-tooling",
    "tooling/semgrep.md": "semgrep-tooling",
    "tooling/agent_browser.md": "browser-exploitation-tooling",
    "tooling/python.md": "python-exploit-runtime",
}

# Platform-only skills to copy as-is (enhanced later if needed)
PLATFORM_ONLY = [
    "xpath-injection-testing",
    "secure-code-review",
    "mobile-app-security-testing",
    "cloud-security-audit",
    "api-security-testing",
    "security-automation",
    "vulnerability-assessment",
    "ldap-injection-testing",
    "container-security-testing",
    "network-penetration-testing",
    "incident-response",
]


def parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
    if not content.startswith("---"):
        return {}, content
    end = content.find("---", 3)
    if end == -1:
        return {}, content
    fm_block = content[3:end].strip()
    body = content[end + 3 :].lstrip("\n")
    meta: dict[str, str] = {}
    for line in fm_block.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip()] = val.strip()
    return meta, body


def build_skill_md(
    name: str,
    description: str,
    exploitation_body: str,
    platform_body: str | None,
) -> str:
    desc = description or f"Professional penetration testing skill: {name}"
    sections = [f"---\nname: {name}\ndescription: {desc}\n---\n"]

    sections.append(f"# {name.replace('-', ' ').title()}\n")
    sections.append(
        "> **penkit51 AI** — professional penetration testing skill pack. "
        "Authorized testing only.\n"
    )

    if exploitation_body.strip():
        sections.append("## Deep Exploitation Guide\n")
        sections.append(exploitation_body.strip())
        sections.append("")

    if platform_body and platform_body.strip():
        sections.append("## Platform Methodology\n")
        sections.append(platform_body.strip())
        sections.append("")

    sections.append("## Validation & Reporting\n")
    sections.append(
        "- Confirm every finding with reproducible PoC before reporting\n"
        "- Document: severity (CVSS), affected asset, steps, evidence, remediation\n"
        "- Use `record_vulnerability` when running inside the penkit51 platform\n"
        "- Chain low-severity findings into higher-impact attack paths\n"
        "- Never report without evidence — distinguish hypothesis from confirmed vuln\n"
    )

    return "\n".join(sections) + "\n"


def extract_cyber_body(skill_dir: Path) -> str | None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return None
    _, body = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    return body


def main() -> None:
    upstream_exploitation, upstream_platform = _upstream_dirs()

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)

    created: list[str] = []

    for upstream_rel, skill_name in EXPLOITATION_MAP.items():
        upstream_path = upstream_exploitation / upstream_rel
        if not upstream_path.exists():
            print(f"SKIP missing upstream skill: {upstream_rel}")
            continue

        upstream_content = upstream_path.read_text(encoding="utf-8")
        upstream_meta, exploitation_body = parse_frontmatter(upstream_content)

        platform_dir = upstream_platform / skill_name
        platform_body = extract_cyber_body(platform_dir) if platform_dir.exists() else None

        desc = upstream_meta.get("description", "")
        out_dir = OUTPUT / skill_name
        out_dir.mkdir(parents=True)
        (out_dir / "SKILL.md").write_text(
            build_skill_md(skill_name, desc, exploitation_body, platform_body),
            encoding="utf-8",
        )
        created.append(skill_name)
        print(f"MERGED: {skill_name}")

    for skill_name in PLATFORM_ONLY:
        src = upstream_platform / skill_name
        if not src.exists():
            continue
        dst = OUTPUT / skill_name
        shutil.copytree(src, dst)
        # Add penkit51 header if not present
        skill_md = dst / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")
        if "penkit51 AI" not in content:
            meta, body = parse_frontmatter(content)
            name = meta.get("name", skill_name)
            desc = meta.get("description", "")
            skill_md.write_text(
                build_skill_md(name, desc, "", body),
                encoding="utf-8",
            )
        created.append(skill_name)
        print(f"COPIED: {skill_name}")

    # Engagement planning skill (new)
    engagement_dir = OUTPUT / "engagement-planning"
    engagement_dir.mkdir()
    (engagement_dir / "SKILL.md").write_text(
        """---
name: engagement-planning
description: Rules of engagement, scope definition, and authorized penetration test planning
---

# Engagement Planning

## Pre-Engagement Checklist

1. **Written authorization** — signed SOW/ROE with explicit in-scope assets
2. **Scope boundaries** — domains, IPs, apps, excluded systems (production DBs, third parties)
3. **Testing window** — dates, hours, blackout periods
4. **Contacts** — technical POC, emergency stop contact
5. **Data handling** — what can be exfiltrated, retention, destruction

## Scope Template

```
IN-SCOPE:
- https://app.example.com (all subpaths)
- api.example.com
- 10.0.0.0/24 (staging only)

OUT-OF-SCOPE:
- Production payment gateway
- Third-party SaaS (Stripe, Auth0)
- Social engineering / phishing
- DoS / availability attacks
```

## Testing Phases

| Phase | Goal | Skills to Load |
|-------|------|----------------|
| Recon | Attack surface map | subfinder-tooling, httpx-tooling, nmap-tooling |
| Enum | Services, endpoints, tech stack | katana-tooling, ffuf-tooling, nuclei-tooling |
| Assess | Vuln discovery | vulnerability-specific skills |
| Exploit | PoC validation | deep-pentest-methodology |
| Report | Findings + remediation | engagement-planning |

## Risk Controls

- Start with passive/low-impact techniques
- Escalate only with evidence of vulnerability
- HITL approval for destructive operations
- Document every action with timestamps
""",
        encoding="utf-8",
    )
    created.append("engagement-planning")

    print(f"\nTotal skills created: {len(created)}")
    (ROOT / "SKILL_MANIFEST.txt").write_text("\n".join(sorted(created)) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()