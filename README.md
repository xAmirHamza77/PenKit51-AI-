<div align="center">

<img src="assets/logo.png" alt="penkit51 AI logo" width="180">

# penkit51 AI

**The open-source AI penetration testing platform with 63 deep exploitation skills, multi-agent orchestration, and cross-platform assistant support.**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/Skills-63-orange.svg)](skills/)
[![Agents](https://img.shields.io/badge/Agents-Multi--Agent-green.svg)](agents/)
[![Platforms](https://img.shields.io/badge/Assistants-Claude%20%7C%20ChatGPT%20%7C%20Grok-purple.svg)](assistant-skills/)

[Features](#features) · [Quick Start](#quick-start) · [Assistant Skills](#assistant-skills) · [Skill Library](#skill-library) · [Architecture](#architecture) · [Disclaimer](#disclaimer)

</div>

---

## About

**penkit51 AI** is a production-ready AI penetration testing framework built for security researchers, bug bounty hunters, red teams, and DevSecOps engineers who need **evidence-backed findings** — not scanner noise.

It combines:
- **63 Agent Skills** — deep exploitation guides covering OWASP Top 10, API security, cloud, frameworks, and tooling playbooks
- **Multi-agent orchestration** — coordinator + specialist sub-agents for recon, enumeration, exploitation, and reporting
- **Cross-platform assistant skills** — native packs for **Claude**, **ChatGPT**, and **Grok** using the Agent Skills open standard
- **PoC-first methodology** — every finding requires reproducible proof-of-concept before reporting
- **Vulnerability chaining** — builds multi-step attack paths that automated scanners miss

### Who is this for?

| Audience | Use Case |
|----------|----------|
| **Penetration testers** | Authorized web/API/cloud assessments with structured methodology |
| **Bug bounty hunters** | Focused vuln-class testing with bypass techniques and validation |
| **Security engineers** | DevSecOps integration, CI/CD security reviews, SAST+DAST workflows |
| **Red teams** | Multi-phase engagements with orchestrated specialist agents |
| **AI assistant users** | Drop-in skills for Claude, ChatGPT, or Grok — no platform lock-in |

---

## Features

### Deep Skill Library (63 packs)

Progressive-disclosure skill packs following the [Agent Skills](https://agentskills.io) standard. Each skill includes attack surface mapping, exploitation techniques, WAF bypass methods, validation steps, and remediation guidance.

### Multi-Agent Orchestration

| Agent | Role |
|-------|------|
| `penkit51-orchestrator` | Master coordinator — plans, delegates, chains findings |
| `vulnerability-hunter` | Deep single-class vuln discovery with PoC validation |
| `recon` | Asset discovery and attack surface mapping |
| `penetration` | Exploitation and impact proof |
| `reporting-remediation` | Professional findings report |

### Assistant Skills (Claude · ChatGPT · Grok)

Platform-native skill packs with slash commands, vulnerability matrix, and report templates:

```
/penkit51-ai plan https://target.com
/penkit51-ai deep https://target.com
/penkit51-ai test https://api.target.com sqli
/penkit51-ai report
```

### Testing Methodology

Three engagement depths:
- **Quick** — CI/CD, PR diff-scoped, time-boxed reviews
- **Standard** — balanced web application assessment
- **Deep** — exhaustive coverage with vulnerability chaining

### Evidence Standards

Every confirmed finding requires:
1. Reproducible PoC with exact steps
2. HTTP request/response evidence
3. Impact statement (attacker outcome)
4. CVSS-based severity reasoning
5. Specific remediation guidance

---

## Quick Start

### Assistant Skills

| Platform | Install |
|----------|---------|
| **Claude** | `cp -R assistant-skills/claude/penkit51-ai ~/.claude/skills/` |
| **ChatGPT** | Upload `dist/penkit51-ai-chatgpt.zip` at [chatgpt.com/skills](https://chatgpt.com/skills) |
| **Grok** | `cp -R assistant-skills/grok/penkit51-ai ~/.grok/skills/` |

```bash
# Package upload zips
./scripts/package-assistant-skills.sh

# Install Claude + Grok locally
./scripts/install-assistant-skills.sh all
```

### Start an Engagement

```
/penkit51-ai deep https://target.com

Scope: all subdomains of target.com
Exclude: payment gateway, production database
Authorization: confirmed — client SOW signed
```

### Use Skill Packs Directly

Point any Agent Skills-compatible runtime at the `skills/` directory. The model loads methodology on demand via progressive disclosure.

### Optional Platform Deployment

```bash
PLATFORM_DIR=/path/to/platform ./scripts/install.sh
```

---

## Skill Library

### Vulnerability Testing (26)
SQLi · XSS · SSRF · CSRF · XXE · IDOR · RCE · SSTI · NoSQLi · Deserialization · File Upload · JWT · Race Conditions · HTTP Smuggling · Prototype Pollution · Mass Assignment · Open Redirect · Header Injection · Path Traversal · Subdomain Takeover · Business Logic · BFLA · Info Disclosure · LLM Prompt Injection · LDAP · XPath

### Framework & Technology (8)
FastAPI · Next.js · Django · NestJS · Supabase · Firebase/Firestore · GraphQL · OAuth

### Cloud & Infrastructure (4)
AWS Audit · Kubernetes · Container Security · Network Penetration

### Methodology (4)
Deep · Standard · Quick pentest modes · Engagement Planning · Orchestration

### Tooling Playbooks (12)
nmap · nuclei · httpx · ffuf · subfinder · naabu · katana · sqlmap · semgrep · Browser Exploitation · Python Exploit Runtime

### Platform (9)
API Security · Code Review · Mobile App · Vulnerability Assessment · Security Automation · Incident Response · Whitebox/SAST · Source-Aware Testing

---

## Architecture

```
penkit51-AI/
├── assets/
│   └── logo.png                 # Project logo
├── skills/                      # 63 Agent Skills (SKILL.md)
├── agents/
│   ├── orchestrator.md          # Master coordinator
│   └── vulnerability-hunter.md  # Deep vuln specialist
├── roles/
│   └── penkit51-ai.yaml         # Pre-configured pentest role
├── assistant-skills/
│   ├── claude/penkit51-ai/      # Claude Code skill
│   ├── chatgpt/penkit51-ai/     # ChatGPT upload skill
│   └── grok/penkit51-ai/         # Grok/Cursor skill
├── dist/                        # Packaged upload zips
└── scripts/
    ├── merge_skills.py
    ├── package-assistant-skills.sh
    └── install-assistant-skills.sh
```

---

## GitHub Repository Description

> **penkit51 AI** — Open-source AI penetration testing platform with 63 deep exploitation skills, multi-agent orchestration, PoC-validated findings, and native assistant skills for Claude, ChatGPT, and Grok. Authorized testing only.

### Suggested Topics
`penetration-testing` `security` `ai` `cybersecurity` `bug-bounty` `owasp` `red-team` `agent-skills` `claude` `chatgpt` `vulnerability-assessment` `devsecops` `sql-injection` `xss` `api-security`

---

## Regenerating Skills

```bash
./scripts/prepare_upstream.sh
python3 scripts/merge_skills.py
python3 scripts/sanitize_names.py
```

---

## Disclaimer

**Authorized testing only.** Use penkit51 AI exclusively on systems you own or have explicit written permission to test. You are solely responsible for ethical and legal compliance. The authors assume no liability for misuse.

---

<div align="center">

**penkit51 AI** — Forge vulnerabilities into validated findings.

</div>