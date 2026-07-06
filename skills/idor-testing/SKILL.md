---
name: idor-testing
description: IDOR/BOLA testing for object-level authorization failures and cross-account data access
---

# Idor Testing

> **penkit51 AI** — professional penetration testing skill pack. Authorized testing only.

## Deep Exploitation Guide

# IDOR

Object-level authorization failures (BOLA/IDOR) lead to cross-account data exposure and unauthorized state changes across APIs, web, mobile, and microservices. Treat every object reference as untrusted until proven bound to the caller.

## Attack Surface

**Scope**
- Horizontal access: access another subject's objects of the same type
- Vertical access: access privileged objects/actions (admin-only, staff-only)
- Cross-tenant access: break isolation boundaries in multi-tenant systems
- Cross-service access: token or context accepted by the wrong service

**Reference Locations**
- Paths, query params, JSON bodies, form-data, headers, cookies
- JWT claims, GraphQL arguments, WebSocket messages, gRPC messages

**Identifier Forms**
- Integers, UUID/ULID/CUID, Snowflake, slugs
- Composite keys (e.g., `{orgId}:{userId}`)
- Opaque tokens, base64/hex-encoded blobs

**Relationship References**
- parentId, ownerId, accountId, tenantId, organization, teamId, projectId, subscriptionId

**Expansion/Projection Knobs**
- `fields`, `include`, `expand`, `projection`, `with`, `select`, `populate`
- Often bypass authorization in resolvers or serializers

## High-Value Targets

- Exports/backups/reporting endpoints (CSV/PDF/ZIP)
- Messaging/mailbox/notifications, audit logs, activity feeds
- Billing: invoices, payment methods, transactions, credits
- Healthcare/education records, HR documents, PII/PHI/PCI
- Admin/staff tools, impersonation/session management
- File/object storage keys (S3/GCS signed URLs, share links)
- Background jobs: import/export job IDs, task results
- Multi-tenant resources: organizations, workspaces, projects

## Reconnaissance

**Parameter Analysis**
- Pagination/cursors: `page[offset]`, `page[limit]`, `cursor`, `nextPageToken` (often reveal or accept cross-tenant/state)
- Directory/list endpoints as seeders: search/list/suggest/export often leak object IDs for secondary exploitation
- Find undocumented params with `arjun -u <url>` (GET) or `arjun -u <url> -m POST` —
  surfaces hidden filters like `?include_deleted=1`, `?as_user=…`, `?owner_id=…`
  that frequently widen the IDOR surface.

**Enumeration Techniques**
- Alternate types: `{"id":123}` vs `{"id":"123"}`, arrays vs scalars, objects vs scalars
- Edge values: null/empty/0/-1/MAX_INT, scientific notation, overflows
- Duplicate keys/parameter pollution: `id=1&id=2`, JSON duplicate keys `{"id":1,"id":2}` (parser precedence)
- Case/aliasing: userId vs userid vs USER_ID; alt names like resourceId, targetId, account
- Path traversal-like in virtual file systems: `/files/user_123/../../user_456/report.csv`

**UUID/Opaque ID Sources**
- Logs, exports, JS bundles, analytics endpoints, emails, public activity
- Time-based IDs (UUIDv1, ULID) may be guessable within a window

## Key Vulnerabilities

### Horizontal & Vertical Access

- Swap object IDs between principals using the same token to probe horizontal access
- Repeat with lower-privilege tokens to probe vertical access
- Target partial updates (PATCH, JSON Patch/JSON Merge Patch) for silent unauthorized modifications

### Bulk & Batch Operations

- Batch endpoints (bulk update/delete) often validate only the first element; include cross-tenant IDs mid-array
- CSV/JSON imports referencing foreign object IDs (ownerId, orgId) may bypass create-time checks

### Secondary IDOR

- Use list/search endpoints, notifications, emails, webhooks, and client logs to collect valid IDs
- Fetch or mutate those objects directly
- Pagination/cursor manipulation to skip filters and pull other users' pages

### Job/Task Objects

- Access job/task IDs from one user to retrieve results for another (`export/{jobId}/download`, `reports/{taskId}`)
- Cancel/approve someone else's jobs by referencing their task IDs

### File/Object Storage

- Direct object paths or weakly scoped signed URLs
- Attempt key prefix changes, content-disposition tricks, or stale signatures reused across tenants
- Replace share tokens with tokens from other tenants; try case/URL-encoding variations

### GraphQL

- Enforce resolver-level checks: do not rely on a top-level gate
- Verify field and edge resolvers bind the resource to the caller on every hop
- Abuse batching/aliases to retrieve multiple users' nodes in one request
- Global node patterns (Relay): decode base64 IDs and swap raw IDs
- Overfetching via fragments on privileged types

```graphql
query IDOR {
  me { id }
  u1: user(id: "VXNlcjo0NTY=") { email billing { last4 } }
  u2: node(id: "VXNlcjo0NTc=") { ... on User { email } }
}
```

### Microservices & Gateways

- Token confusion: token scoped for Service A accepted by Service B due to shared JWT verification but missing audience/claims checks
- Trust on headers: reverse proxies or API gateways injecting/trusting headers like `X-User-Id`, `X-Organization-Id`; try overriding or removing them
- Context loss: async consumers (queues, workers) re-process requests without re-checking authorization

### Multi-Tenant

- Probe tenant scoping through headers, subdomains, and path params (`X-Tenant-ID`, org slug)
- Try mixing org of token with resource from another org
- Test cross-tenant reports/analytics rollups and admin views which aggregate multiple tenants

### WebSocket

- Authorization per-subscription: ensure channel/topic names cannot be guessed (`user_{id}`, `org_{id}`)
- Subscribe/publish checks must run server-side, not only at handshake
- Try sending messages with target user IDs after subscribing to own channels

### gRPC

- Direct protobuf fields (`owner_id`, `tenant_id`) often bypass HTTP-layer middleware
- Validate references via grpcurl with tokens from different principals

### Integrations

- Webhooks/callbacks referencing foreign objects (e.g., `invoice_id`) processed without verifying ownership
- Third-party importers syncing data into wrong tenant due to missing tenant binding

## Bypass Techniques

**Parser & Transport**
- Content-type switching: `application/json` ↔ `application/x-www-form-urlencoded` ↔ `multipart/form-data`
- Method tunneling: `X-HTTP-Method-Override`, `_method=PATCH`; or using GET on endpoints incorrectly accepting state changes
- JSON duplicate keys/array injection to bypass naive validators

**Parameter Pollution**
- Duplicate parameters in query/body to influence server-side precedence (`id=123&id=456`); try both orderings
- Mix case/alias param names so gateway and backend disagree (userId vs userid)

**Cache & Gateway**
- CDN/proxy key confusion: responses keyed without Authorization or tenant headers expose cached objects to other users
- Manipulate Vary and Accept headers
- Redirect chains and 304/206 behaviors can leak content across tenants

**Race Windows**
- Time-of-check vs time-of-use: change the referenced ID between validation and execution using parallel requests

**Blind Channels**
- Use differential responses (status, size, ETag, timing) to detect existence
- Error shape often differs for owned vs foreign objects
- HEAD/OPTIONS, conditional requests (`If-None-Match`/`If-Modified-Since`) can confirm existence without full content

## Chaining Attacks

- IDOR + CSRF: force victims to trigger unauthorized changes on objects you discovered
- IDOR + Stored XSS: pivot into other users' sessions through data you gained access to
- IDOR + SSRF: exfiltrate internal IDs, then access their corresponding resources
- IDOR + Race: bypass spot checks with simultaneous requests

## Testing Methodology

1. **Build matrix** - Subject × Object × Action matrix (who can do what to which resource)
2. **Obtain principals** - At least two: owner and non-owner (plus admin/staff if applicable)
3. **Collect IDs** - Capture at least one valid object ID per principal from list/search/export endpoints
4. **Cross-channel testing** - Exercise every action (R/W/D/Export) while swapping IDs, tokens, tenants
5. **Transport variation** - Test across web, mobile, API, GraphQL, WebSocket, gRPC
6. **Consistency check** - Same rule must hold regardless of transport, content-type, serialization, or gateway

## Validation

1. Demonstrate access to an object not owned by the caller (content or metadata)
2. Show the same request fails with appropriately enforced authorization when corrected
3. Prove cross-channel consistency: same unauthorized access via at least two transports (e.g., REST and GraphQL)
4. Document tenant boundary violations (if applicable)
5. Provide reproducible steps and evidence (requests/responses for owner vs non-owner)

## False Positives

- Public/anonymous resources by design
- Soft-privatized data where content is already public
- Idempotent metadata lookups that do not reveal sensitive content
- Correct row-level checks enforced across all channels
- Empty array / null returned for another user's resource — silent enforcement, not exposure; compare against the owner's view to confirm the data is actually missing rather than just hidden from the response shape

## Impact

- Cross-account data exposure (PII/PHI/PCI)
- Unauthorized state changes (transfers, role changes, cancellations)
- Cross-tenant data leaks violating contractual and regulatory boundaries
- Regulatory risk (GDPR/HIPAA/PCI), fraud, reputational damage

## Pro Tips

1. Always test list/search/export endpoints first; they are rich ID seeders
2. Build a reusable ID corpus from logs, notifications, emails, and client bundles
3. Toggle content-types and transports; authorization middleware often differs per stack
4. In GraphQL, validate at resolver boundaries; never trust parent auth to cover children
5. In multi-tenant apps, vary org headers, subdomains, and path params independently
6. Check batch/bulk operations and background job endpoints; they frequently skip per-item checks
7. Inspect gateways for header trust and cache key configuration
8. Treat UUIDs as untrusted; obtain them via OSINT/leaks and test binding
9. Use timing/size/ETag differentials for blind confirmation when content is masked
10. Prove impact with precise before/after diffs and role-separated evidence

## Summary

Authorization must bind subject, action, and specific object on every request, regardless of identifier opacity or transport. If the binding is missing anywhere, the system is vulnerable.

## Platform Methodology

# IDOR不安全的直接对象引用测试

## 概述

IDOR（Insecure Direct Object Reference）是一种访问控制漏洞，当应用程序直接使用用户提供的输入来访问资源，而未验证用户是否有权限访问该资源时发生。本技能提供IDOR漏洞的检测、利用和防护方法。

## 漏洞原理

应用程序使用可预测的标识符（如ID、文件名）直接引用资源，未验证当前用户是否有权限访问该资源。

**危险代码示例：**
```php
// 直接使用用户输入的ID
$file = file_get_contents('/files/' . $_GET['id'] . '.pdf');
```

## 测试方法

### 1. 识别直接对象引用

**常见资源类型：**
- 用户ID
- 文件ID/文件名
- 订单ID
- 文档ID
- 账户ID
- 记录ID

**常见位置：**
- URL参数
- POST数据
- Cookie值
- HTTP头
- 文件路径

### 2. 枚举测试

**顺序ID测试：**
```
/user?id=1
/user?id=2
/user?id=3
```

**UUID测试：**
```
/user?id=550e8400-e29b-41d4-a716-446655440000
/user?id=550e8400-e29b-41d4-a716-446655440001
```

**文件名测试：**
```
/files/document1.pdf
/files/document2.pdf
/files/invoice_2024_001.pdf
```

### 3. 水平权限测试

**访问其他用户资源：**
```
当前用户ID: 100
测试: /user?id=101
测试: /user?id=102
```

**访问其他用户文件：**
```
/files/user100_document.pdf
测试: /files/user101_document.pdf
```

### 4. 垂直权限测试

**普通用户访问管理员资源：**
```
/admin/users?id=1
/admin/settings
/admin/logs
```

## 利用技术

### 用户信息泄露

**枚举用户资料：**
```bash
# 顺序枚举
for i in {1..1000}; do
  curl "https://target.com/user?id=$i"
done

# 观察响应差异
```

### 文件访问

**访问其他用户文件：**
```
/files/invoice_12345.pdf
/files/report_67890.pdf
/files/contract_11111.pdf
```

**目录遍历结合：**
```
/files/../admin/config.php
/files/../../etc/passwd
```

### 数据修改

**修改其他用户数据：**
```http
POST /api/user/update
Content-Type: application/json

{
  "id": 101,
  "email": "attacker@evil.com"
}
```

### 批量操作

**批量获取数据：**
```python
import requests

for user_id in range(1, 1000):
    response = requests.get(f'https://target.com/api/user/{user_id}')
    if response.status_code == 200:
        print(f"User {user_id}: {response.json()}")
```

## 绕过技术

### ID混淆

**Base64编码：**
```
原始ID: 123
编码: MTIz
URL: /user?id=MTIz
```

**哈希值：**
```
原始ID: 123
哈希: 202cb962ac59075b964b07152d234b70
URL: /user?id=202cb962ac59075b964b07152d234b70
```

### 参数名混淆

**使用不同参数名：**
```
/user?id=123
/user?uid=123
/user?user_id=123
/user?account=123
```

### HTTP方法绕过

**尝试不同HTTP方法：**
```
GET /user/123
POST /user/123
PUT /user/123
PATCH /user/123
```

### 路径混淆

**尝试不同路径：**
```
/api/v1/user/123
/api/user/123
/user/123
/users/123
```

## 工具使用

### Burp Suite

**使用Intruder：**
1. 拦截请求
2. 发送到Intruder
3. 标记ID参数
4. 使用数字序列或自定义列表
5. 观察响应差异

**使用Repeater：**
1. 手动修改ID
2. 测试不同值
3. 观察响应

### OWASP ZAP

```bash
# 使用ZAP进行IDOR扫描
zap-cli active-scan --scanners all http://target.com
```

### Python脚本

```python
import requests
import json

def test_idor(base_url, user_id_range):
    for user_id in user_id_range:
        url = f"{base_url}/user?id={user_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"User {user_id}: {data.get('email', 'N/A')}")

test_idor("https://target.com", range(1, 100))
```

## 验证和报告

### 验证步骤

1. 确认可以访问未授权的资源
2. 验证可以读取、修改或删除其他用户数据
3. 评估影响（数据泄露、隐私侵犯等）
4. 记录完整的POC

### 报告要点

- 漏洞位置和资源标识符
- 可访问的未授权资源
- 完整的利用步骤和PoC
- 修复建议（访问控制、资源映射等）

## 防护措施

### 推荐方案

1. **访问控制验证**
   ```python
   def get_user_data(user_id, current_user_id):
       # 验证权限
       if user_id != current_user_id:
           raise PermissionDenied("Cannot access other user's data")
       
       # 返回数据
       return db.get_user(user_id)
   ```

2. **间接对象引用**
   ```python
   # 使用映射表
   user_mapping = {
       'abc123': 100,
       'def456': 101,
       'ghi789': 102
   }
   
   def get_user(mapped_id):
       real_id = user_mapping.get(mapped_id)
       if not real_id:
           raise NotFound()
       return db.get_user(real_id)
   ```

3. **基于角色的访问控制**
   ```python
   def check_permission(user, resource):
       if user.role == 'admin':
           return True
       if resource.owner_id == user.id:
           return True
       return False
   ```

4. **资源所有权验证**
   ```python
   def update_user_data(user_id, data, current_user):
       user = db.get_user(user_id)
       
       # 验证所有权
       if user.id != current_user.id and current_user.role != 'admin':
           raise PermissionDenied()
       
       # 更新数据
       db.update_user(user_id, data)
   ```

5. **使用不可预测的标识符**
   ```python
   import uuid
   
   # 使用UUID替代顺序ID
   resource_id = str(uuid.uuid4())
   ```

6. **最小权限原则**
   - 只返回用户有权限访问的数据
   - 使用数据过滤
   - 限制可访问的资源范围

## 注意事项

- 仅在授权测试环境中进行
- 避免访问或修改真实用户数据
- 注意不同资源的访问控制差异
- 测试时注意请求频率，避免触发防护

## Validation & Reporting

- Confirm every finding with reproducible PoC before reporting
- Document: severity (CVSS), affected asset, steps, evidence, remediation
- Use `record_vulnerability` when running inside the penkit51 platform
- Chain low-severity findings into higher-impact attack paths
- Never report without evidence — distinguish hypothesis from confirmed vuln

