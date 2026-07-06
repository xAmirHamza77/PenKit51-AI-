---
name: csrf-testing
description: CSRF testing covering token bypass, SameSite cookies, CORS misconfigurations, and state-changing request abuse
---

# Csrf Testing

> **penkit51 AI** — professional penetration testing skill pack. Authorized testing only.

## Deep Exploitation Guide

# CSRF

Cross-site request forgery abuses ambient authority (cookies, HTTP auth) across origins. Do not rely on CORS alone; enforce non-replayable tokens and strict origin checks for every state change.

## Attack Surface

**Session Types**
- Web apps with cookie-based sessions and HTTP auth
- JSON/REST, GraphQL (GET/persisted queries), file upload endpoints

**Authentication Flows**
- Login/logout, password/email change, MFA toggles

**OAuth/OIDC**
- Authorize, token, logout, disconnect/connect endpoints

## High-Value Targets

- Credentials and profile changes (email/password/phone)
- Payment and money movement, subscription/plan changes
- API key/secret generation, PAT rotation, SSH keys
- 2FA/TOTP enable/disable; backup codes; device trust
- OAuth connect/disconnect; logout; account deletion
- Admin/staff actions and impersonation flows
- File uploads/deletes; access control changes

## Reconnaissance

### Session and Cookies

- Inspect cookies: HttpOnly, Secure, SameSite (Strict/Lax/None)
- Lax allows cookies on top-level cross-site GET; None requires Secure
- Determine if Authorization headers or bearer tokens are used (generally not CSRF-prone) versus cookies (CSRF-prone)

### Token and Header Checks

- Locate anti-CSRF tokens (hidden inputs, meta tags, custom headers)
- Test removal, reuse across requests, reuse across sessions, binding to method/path
- Verify server checks Origin and/or Referer on state changes
- Test null/missing and cross-origin values

### Method and Content-Types

- Confirm whether GET, HEAD, or OPTIONS perform state changes
- Try simple content-types to avoid preflight: `application/x-www-form-urlencoded`, `multipart/form-data`, `text/plain`
- Probe parsers that auto-coerce `text/plain` or form-encoded bodies into JSON

### CORS Profile

- Identify `Access-Control-Allow-Origin` and `-Credentials`
- Overly permissive CORS is not a CSRF fix and can turn CSRF into data exfiltration
- Test per-endpoint CORS differences; preflight vs simple request behavior can diverge

## Key Vulnerabilities

### Navigation CSRF

- Auto-submitting form to target origin; works when cookies are sent and no token/origin checks are enforced
- Top-level GET navigation can trigger state if server misuses GET or links actions to GET callbacks

### Simple Content-Type CSRF

- `application/x-www-form-urlencoded` and `multipart/form-data` POSTs do not require preflight
- `text/plain` form bodies can slip through validators and be parsed server-side

### JSON CSRF

- If server parses JSON from `text/plain` or form-encoded bodies, craft parameters to reconstruct JSON
- Some frameworks accept JSON keys via form fields (e.g., `data[foo]=bar`) or treat duplicate keys leniently

### Login/Logout CSRF

- Force logout to clear CSRF tokens, then chain login CSRF to bind victim to attacker's account
- Login CSRF: submit attacker credentials to victim's browser; later actions occur under attacker's account

### OAuth/OIDC Flows

- Abuse authorize/logout endpoints reachable via GET or form POST without origin checks
- Exploit relaxed SameSite on top-level navigations
- Open redirects or loose redirect_uri validation can chain with CSRF to force unintended authorizations

### File and Action Endpoints

- File upload/delete often lack token checks; forge multipart requests to modify storage
- Admin actions exposed as simple POST links are frequently CSRFable

### GraphQL CSRF

- If queries/mutations are allowed via GET or persisted queries, exploit top-level navigation with encoded payloads
- Batched operations may hide mutations within a nominally safe request

### WebSocket CSRF

- Browsers send cookies on WebSocket handshake
- Enforce Origin checks server-side; without them, cross-site pages can open authenticated sockets and issue actions

## Bypass Techniques

### SameSite Nuance

- Lax-by-default cookies are sent on top-level cross-site GET but not POST
- Exploit GET state changes and GET-based confirmation steps
- Legacy or nonstandard clients may ignore SameSite; validate across browsers/devices

### Origin/Referer Obfuscation

- Sandbox/iframes can produce null Origin; some frameworks incorrectly accept null
- `about:blank`/`data:` URLs alter Referer
- Ensure server requires explicit Origin/Referer match

### Method Override

- Backends honoring `_method` or `X-HTTP-Method-Override` may allow destructive actions through a simple POST

### Token Weaknesses

- Accepting missing/empty tokens
- Tokens not tied to session, user, or path
- Tokens reused indefinitely; tokens in GET
- Double-submit cookie without Secure/HttpOnly, or with predictable token sources

### Content-Type Switching

- Switch between form, multipart, and `text/plain` to reach different code paths
- Use duplicate keys and array shapes to confuse parsers

### Header Manipulation

- Strip Referer via meta refresh or navigate from `about:blank`
- Test null Origin acceptance
- Leverage misconfigured CORS to add custom headers that servers mistakenly treat as CSRF tokens

## Special Contexts

### Mobile/SPA

- Deep links and embedded WebViews may auto-send cookies; trigger actions via crafted intents/links
- SPAs that rely solely on bearer tokens are less CSRF-prone, but hybrid apps mixing cookies and APIs can still be vulnerable

### Integrations

- Webhooks and back-office tools sometimes expose state-changing GETs intended for staff
- Confirm CSRF defenses there too

## Chaining Attacks

- CSRF + IDOR: force actions on other users' resources once references are known
- CSRF + Clickjacking: guide user interactions to bypass UI confirmations
- CSRF + OAuth mix-up: bind victim sessions to unintended clients

## Testing Methodology

1. **Inventory endpoints** - All state-changing endpoints including admin/staff
2. **Note request details** - Method, content-type, whether reachable via simple requests
3. **Assess session model** - Cookies with SameSite attrs, custom headers, tokens
4. **Check defenses** - Anti-CSRF tokens and Origin/Referer enforcement
5. **Attempt preflightless delivery** - Form POST, text/plain, multipart/form-data
6. **Test navigation** - Top-level GET navigation
7. **Cross-browser validation** - Behavior differs by SameSite and navigation context

## Validation

1. Demonstrate a cross-origin page that triggers a state change without user interaction beyond visiting
2. Show that removing the anti-CSRF control (token/header) is accepted, or that Origin/Referer are not verified
3. Prove behavior across at least two browsers or contexts (top-level nav vs XHR/fetch)
4. Provide before/after state evidence for the same account
5. If defenses exist, show the exact condition under which they are bypassed (content-type, method override, null Origin)

## False Positives

- Token verification present and required; Origin/Referer enforced consistently
- No cookies sent on cross-site requests (SameSite=Strict, no HTTP auth) and no state change via simple requests
- Only idempotent, non-sensitive operations affected

## Impact

- Account state changes (email/password/MFA), session hijacking via login CSRF
- Financial operations, administrative actions
- Durable authorization changes (role/permission flips, key rotations) and data loss

## Pro Tips

1. Prefer preflightless vectors (form-encoded, multipart, text/plain) and top-level GET if available
2. Test login/logout, OAuth connect/disconnect, and account linking first
3. Validate Origin/Referer behavior explicitly; do not assume frameworks enforce them
4. Toggle SameSite and observe differences across navigation vs XHR
5. For GraphQL, attempt GET queries or persisted queries that carry mutations
6. Always try method overrides and parser differentials
7. Combine with clickjacking when visual confirmations block CSRF

## Summary

CSRF is eliminated only when state changes require a secret the attacker cannot supply and the server verifies the caller's origin. Tokens and Origin checks must hold across methods, content-types, and transports.

## Platform Methodology

# CSRF跨站请求伪造测试

## 概述

CSRF（Cross-Site Request Forgery）是一种利用用户已登录状态进行未授权操作的攻击方式。本技能提供CSRF漏洞的检测、利用和防护方法。

## 漏洞原理

- 攻击者诱导用户访问恶意页面
- 恶意页面自动发送请求到目标网站
- 浏览器自动携带用户的认证信息（Cookie、Session）
- 目标网站误认为是用户合法操作

## 测试方法

### 1. 识别敏感操作

- 密码修改
- 邮箱修改
- 转账操作
- 权限变更
- 数据删除
- 状态更新

### 2. 检测CSRF Token

**检查是否有Token保护：**
```html
<!-- 有Token保护 -->
<form method="POST" action="/change-password">
  <input type="hidden" name="csrf_token" value="abc123">
  <input type="password" name="new_password">
</form>

<!-- 无Token保护 - 存在CSRF风险 -->
<form method="POST" action="/change-email">
  <input type="email" name="new_email">
</form>
```

### 3. 验证Token有效性

**测试Token是否可预测：**
- Token是否基于时间戳
- Token是否基于用户ID
- Token是否可重复使用
- Token是否在多个请求间共享

### 4. 检查Referer验证

**测试Referer检查是否可绕过：**
```javascript
// 正常请求
Referer: https://target.com/change-password

// 测试绕过
Referer: https://target.com.evil.com
Referer: https://evil.com/?target.com
Referer: (空)
```

## 利用技术

### 基础CSRF攻击

**HTML表单自动提交：**
```html
<form action="https://target.com/api/transfer" method="POST" id="csrf">
  <input type="hidden" name="to" value="attacker_account">
  <input type="hidden" name="amount" value="10000">
</form>
<script>document.getElementById('csrf').submit();</script>
```

### JSON CSRF

**绕过Content-Type检查：**
```html
<!-- 使用form表单提交JSON -->
<form action="https://target.com/api/update" method="POST" enctype="text/plain">
  <input name='{"email":"attacker@evil.com","ignore":"' value='"}'>
</form>
<script>document.forms[0].submit();</script>
```

### GET请求CSRF

**利用GET请求进行攻击：**
```html
<img src="https://target.com/api/delete?id=123">
```

## 绕过技术

### Token绕过

**如果Token在Cookie中：**
```javascript
// 如果Token同时存在于Cookie和表单中
// 可以尝试只提交Cookie中的Token
fetch('https://target.com/api/action', {
  method: 'POST',
  credentials: 'include',
  body: 'action=delete&id=123'
  // 不包含csrf_token参数，依赖Cookie
});
```

### SameSite Cookie绕过

**利用子域名：**
- 如果SameSite=Lax，GET请求仍可携带Cookie
- 利用子域名进行攻击

### 双重提交Cookie

**绕过Token验证：**
```html
<!-- 如果Token在Cookie中，且验证逻辑有缺陷 -->
<form action="https://target.com/api/action" method="POST">
  <input type="hidden" name="csrf_token" value="">
  <script>
    // 从Cookie中读取Token
    document.cookie.split(';').forEach(c => {
      if(c.trim().startsWith('csrf_token=')) {
        document.querySelector('input[name="csrf_token"]').value = 
          c.split('=')[1];
      }
    });
  </script>
</form>
```

## 工具使用

### Burp Suite

**使用CSRF PoC生成器：**
1. 拦截目标请求
2. 右键 → Engagement tools → Generate CSRF PoC
3. 测试生成的PoC

### OWASP ZAP

```bash
# 使用ZAP进行CSRF扫描
zap-cli quick-scan --self-contained --start-options '-config api.disablekey=true' http://target.com
```

## 验证和报告

### 验证步骤

1. 确认目标操作没有CSRF Token保护
2. 构造恶意请求并验证可执行
3. 评估影响（数据泄露、权限提升、资金损失等）
4. 记录完整的POC

### 报告要点

- 漏洞位置和受影响的操作
- 攻击场景和影响范围
- 完整的利用步骤和PoC
- 修复建议（CSRF Token、SameSite Cookie、Referer验证等）

## 防护措施

### 推荐方案

1. **CSRF Token**
   - 每个表单包含唯一Token
   - Token存储在Session中
   - 验证Token有效性

2. **SameSite Cookie**
   ```javascript
   Set-Cookie: session=abc123; SameSite=Strict; Secure
   ```

3. **双重提交Cookie**
   - Token同时存在于Cookie和表单
   - 验证两者是否匹配

4. **Referer验证**
   - 验证Referer是否为同源
   - 注意空Referer的处理

## 注意事项

- 仅在授权测试环境中进行
- 避免对用户账户造成实际影响
- 记录所有测试步骤
- 考虑不同浏览器的行为差异

## Validation & Reporting

- Confirm every finding with reproducible PoC before reporting
- Document: severity (CVSS), affected asset, steps, evidence, remediation
- Use `record_vulnerability` when running inside the penkit51 platform
- Chain low-severity findings into higher-impact attack paths
- Never report without evidence — distinguish hypothesis from confirmed vuln

