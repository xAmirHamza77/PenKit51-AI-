---
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
