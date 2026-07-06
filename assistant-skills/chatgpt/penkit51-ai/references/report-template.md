# Penetration Test Report Template

```markdown
# Penetration Test Report

**Client**: [Organization]
**Target**: [URLs/IPs/domains tested]
**Assessment Type**: [Black-box | Grey-box | White-box]
**Date**: [Start] – [End]
**Tester**: penkit51 AI
**Classification**: [Confidential]

---

## 1. Executive Summary

[2-4 paragraphs: overall security posture, critical risks, business impact]

**Risk Rating**: [Critical / High / Medium / Low / Informational]

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |
| Info | 0 |

---

## 2. Scope

### In Scope
- [asset list]

### Out of Scope
- [excluded assets and test types]

### Rules of Engagement
- [authorization reference, testing window, constraints]

---

## 3. Methodology

1. Planning & scoping
2. Reconnaissance (passive + active)
3. Enumeration & attack surface mapping
4. Vulnerability assessment (manual + automated)
5. Exploitation & PoC validation
6. Vulnerability chaining analysis
7. Reporting & remediation guidance

**Tools Used**: [nmap, nuclei, ffuf, sqlmap, etc.]

---

## 4. Findings Summary

| ID | Title | Severity | CVSS | Status |
|----|-------|----------|------|--------|
| PF-001 | [Title] | High | 8.1 | Open |

---

## 5. Detailed Findings

### PF-001: [Vulnerability Title]

| Field | Value |
|-------|-------|
| **Severity** | High |
| **CVSS 3.1** | 8.1 (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N) |
| **CWE** | CWE-89: SQL Injection |
| **OWASP** | A03:2021 – Injection |
| **Location** | `https://target.com/api/users?id=1` |
| **Parameter** | `id` (GET) |

#### Description
[What the vulnerability is and why it exists]

#### Proof of Concept
```
Step 1: Send request...
Step 2: Observe response...
Step 3: Confirm impact...
```

#### Evidence
```http
GET /api/users?id=1' OR 1=1-- HTTP/1.1
Host: target.com

HTTP/1.1 200 OK
[response showing all users returned]
```

#### Impact
[Concrete business/technical impact]

#### Remediation
1. [Specific fix #1]
2. [Specific fix #2]

#### References
- https://cwe.mitre.org/data/definitions/89.html
- https://owasp.org/www-community/attacks/SQL_Injection

---

## 6. Attack Chains

### Chain 1: [Name]
```
[IDOR on /api/profile] → [Admin role in JWT] → [Full data access]
```

---

## 7. Recommendations (Prioritized)

### Immediate (0-7 days)
- [ ] [Critical fix]

### Short-term (7-30 days)
- [ ] [High severity fixes]

### Long-term (30-90 days)
- [ ] [Architecture improvements]

---

## 8. Appendix

### A. Tools & Versions
### B. Raw Scan Outputs (summarized)
### C. Retest Criteria
```
Each finding is considered fixed when:
- PoC no longer reproduces
- Compensating controls verified
```
```