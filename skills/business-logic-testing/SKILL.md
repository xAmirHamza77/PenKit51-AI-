---
name: business-logic-testing
description: Business logic testing for workflow bypass, state manipulation, and domain invariant violations
---

# Business Logic Testing

> **penkit51 AI** — professional penetration testing skill pack. Authorized testing only.

## Deep Exploitation Guide

# Business Logic Flaws

Business logic flaws exploit intended functionality to violate domain invariants: move money without paying, exceed limits, retain privileges, or bypass reviews. They require a model of the business, not just payloads.

## Attack Surface

- Financial logic: pricing, discounts, payments, refunds, credits, chargebacks
- Account lifecycle: signup, upgrade/downgrade, trial, suspension, deletion
- Authorization-by-logic: feature gates, role transitions, approval workflows
- Quotas/limits: rate/usage limits, inventory, entitlements, seat licensing
- Multi-tenant isolation: cross-organization data or action bleed
- Event-driven flows: jobs, webhooks, sagas, compensations, idempotency

## High-Value Targets

- Pricing/cart: price locks, quote to order, tax/shipping computation
- Discount engines: stacking, mutual exclusivity, scope (cart vs item), once-per-user enforcement
- Payments: auth/capture/void/refund sequences, partials, split tenders, chargebacks, idempotency keys
- Credits/gift cards/vouchers: issuance, redemption, reversal, expiry, transferability
- Subscriptions: proration, upgrade/downgrade, trial extension, seat counts, meter reporting
- Refunds/returns/RMAs: multi-item partials, restocking fees, return window edges
- Admin/staff operations: impersonation, manual adjustments, credit/refund issuance, account flags
- Quotas/limits: daily/monthly usage, inventory reservations, feature usage counters

## Reconnaissance

### Workflow Mapping

- Derive endpoints from the UI and proxy/network logs; map hidden/undocumented API calls, especially finalize/confirm endpoints
- Identify tokens/flags: stepToken, paymentIntentId, orderStatus, reviewState, approvalId; test reuse across users/sessions
- Document invariants: conservation of value (ledger balance), uniqueness (idempotency), monotonicity (non-decreasing counters), exclusivity (one active subscription)

### Input Surface

- Hidden fields and client-computed totals; server must recompute on trusted sources
- Alternate encodings and shapes: arrays instead of scalars, objects with unexpected keys, null/empty/0/negative, scientific notation
- Business selectors: currency, locale, timezone, tax region; vary to trigger rounding and ruleset changes

### State and Time Axes

- Replays: resubmit stale finalize/confirm requests
- Out-of-order: call finalize before verify; refund before capture; cancel after ship
- Time windows: end-of-day/month cutovers, daylight saving, grace periods, trial expiry edges

## Key Vulnerabilities

### State Machine Abuse

- Skip or reorder steps via direct API calls; verify server enforces preconditions on each transition
- Replay prior steps with altered parameters (e.g., swap price after approval but before capture)
- Split a single constrained action into many sub-actions under the threshold (limit slicing)

### Concurrency and Idempotency

- Parallelize identical operations to bypass atomic checks (create, apply, redeem, transfer)
- Abuse idempotency: key scoped to path but not principal → reuse other users' keys; or idempotency stored only in cache
- Message reprocessing: queue workers re-run tasks on retry without idempotent guards; cause duplicate fulfillment/refund

### Numeric and Currency

- Floating point vs decimal rounding; rounding/truncation favoring attacker at boundaries
- Cross-currency arbitrage: buy in currency A, refund in B at stale rates; tax rounding per-item vs per-order
- Negative amounts, zero-price, free shipping thresholds, minimum/maximum guardrails

### Quotas, Limits, and Inventory

- Off-by-one and time-bound resets (UTC vs local); pre-warm at T-1s and post-fire at T+1s
- Reservation/hold leaks: reserve multiple, complete one, release not enforced; backorder logic inconsistencies
- Distributed counters without strong consistency enabling double-consumption

### Refunds and Chargebacks

- Double-refund: refund via UI and support tool; refund partials summing above captured amount
- Refund after benefits consumed (downloaded digital goods, shipped items) due to missing post-consumption checks

### Feature Gates and Roles

- Feature flags enforced client-side or at edge but not in core services; toggle names guessed or fallback to default-enabled
- Role transitions leaving stale capabilities (retain premium after downgrade; retain admin endpoints after demotion)

## Advanced Techniques

### Event-Driven Sagas

- Saga/compensation gaps: trigger compensation without original success; or execute success twice without compensation
- Outbox/Inbox patterns missing idempotency → duplicate downstream side effects
- Cron/backfill jobs operating outside request-time authorization; mutate state broadly

### Microservices Boundaries

- Cross-service assumption mismatch: one service validates total, another trusts line items; alter between calls
- Header trust: internal services trusting X-Role or X-User-Id from untrusted edges
- Partial failure windows: two-phase actions where phase 1 commits without phase 2, leaving exploitable intermediate state

### Multi-Tenant Isolation

- Tenant-scoped counters and credits updated without tenant key in the where-clause; leak across orgs
- Admin aggregate views allowing actions that impact other tenants due to missing per-tenant enforcement

## Bypass Techniques

- Content-type switching (JSON/form/multipart) to hit different code paths
- Method alternation (GET performing state change; overrides via X-HTTP-Method-Override)
- Client recomputation: totals, taxes, discounts computed on client and accepted by server
- Cache/gateway differentials: stale decisions from CDN/APIM that are not identity-aware

## Special Contexts

### E-commerce

- Stack incompatible discounts via parallel apply; remove qualifying item after discount applied; retain free shipping after cart changes
- Modify shipping tier post-quote; abuse returns to keep product and refund

### Banking/Fintech

- Split transfers to bypass per-transaction threshold; schedule vs instant path inconsistencies
- Exploit grace periods on holds/authorizations to withdraw again before settlement

### SaaS/B2B

- Seat licensing: race seat assignment to exceed purchased seats; stale license checks in background tasks
- Usage metering: report late or duplicate usage to avoid billing or to over-consume

## Chaining Attacks

- Business logic + race: duplicate benefits before state updates
- Business logic + IDOR: operate on others' resources once a workflow leak reveals IDs
- Business logic + CSRF: force a victim to complete a sensitive step sequence

## Testing Methodology

1. **Enumerate state machine** - Per critical workflow (states, transitions, pre/post-conditions); note invariants
2. **Build Actor × Action × Resource matrix** - Unauth, basic user, premium, staff/admin; identify actions per role
3. **Test transitions** - Step skipping, repetition, reordering, late mutation
4. **Introduce variance** - Time, concurrency, channel (mobile/web/API/GraphQL), content-types
5. **Validate persistence boundaries** - All services, queues, and jobs re-enforce invariants

## Validation

1. Show an invariant violation (e.g., two refunds for one charge, negative inventory, exceeding quotas)
2. Provide side-by-side evidence for intended vs abused flows with the same principal
3. Demonstrate durability: the undesired state persists and is observable in authoritative sources (ledger, emails, admin views)
4. Quantify impact per action and at scale (unit loss × feasible repetitions)

## False Positives

- Promotional behavior explicitly allowed by policy (documented free trials, goodwill credits)
- Visual-only inconsistencies with no durable or exploitable state change
- Admin-only operations with proper audit and approvals

## Impact

- Direct financial loss (fraud, arbitrage, over-refunds, unpaid consumption)
- Regulatory/contractual violations (billing accuracy, consumer protection)
- Denial of inventory/services to legitimate users through resource exhaustion
- Privilege retention or unauthorized access to premium features

## Pro Tips

1. Start from invariants and ledgers, not UI—prove conservation of value breaks
2. Test with time and concurrency; many bugs only appear under pressure
3. Recompute totals server-side; never accept client math—flag when you observe otherwise
4. Treat idempotency and retries as first-class: verify key scope and persistence
5. Probe background workers and webhooks separately; they often skip auth and rule checks
6. Validate role/feature gates at the service that mutates state, not only at the edge
7. Explore end-of-period edges (month-end, trial end, DST) for rounding and window issues
8. Use minimal, auditable PoCs that demonstrate durable state change and exact loss
9. Chain with authorization tests (IDOR/Function-level access) to magnify impact
10. When in doubt, map the state machine; gaps appear where transitions lack server-side guards

## Summary

Business logic security is the enforcement of domain invariants under adversarial sequencing, timing, and inputs. If any step trusts the client or prior steps, expect abuse.

## Platform Methodology

# 业务逻辑漏洞测试

## 概述

业务逻辑漏洞是应用程序在业务处理流程中的设计缺陷，可能导致未授权操作、数据篡改、资金损失等。本技能提供业务逻辑漏洞的检测、利用和防护方法。

## 漏洞类型

### 1. 工作流绕过

**跳过验证步骤：**
- 直接访问最终步骤
- 修改步骤顺序
- 重复执行步骤

### 2. 价格操作

**负数价格：**
- 输入负数金额
- 导致账户余额增加

**价格篡改：**
- 修改前端价格
- 修改API请求中的价格

### 3. 数量限制绕过

**负数数量：**
- 输入负数
- 可能导致库存增加

**超出限制：**
- 修改数量限制
- 批量操作绕过

### 4. 时间竞争

**并发请求：**
- 同时发送多个请求
- 绕过单次限制

### 5. 状态操作

**状态回退：**
- 将已完成订单改为待支付
- 修改订单状态

## 测试方法

### 1. 工作流分析

**识别业务流程：**
- 注册流程
- 购买流程
- 提现流程
- 审核流程

**测试步骤跳过：**
```
正常流程: 步骤1 → 步骤2 → 步骤3
测试: 直接访问步骤3
测试: 步骤1 → 步骤3（跳过步骤2）
```

### 2. 参数篡改

**修改关键参数：**
```http
POST /api/purchase
{
  "product_id": 123,
  "quantity": 1,
  "price": 100.00  # 修改为 0.01
}
```

**负数测试：**
```json
{
  "quantity": -1,
  "price": -100.00
}
```

### 3. 并发测试

**同时发送请求：**
```python
import threading
import requests

def purchase():
    requests.post('https://target.com/api/purchase', 
                  json={'product_id': 123, 'quantity': 1})

# 同时发送10个请求
for i in range(10):
    threading.Thread(target=purchase).start()
```

### 4. 状态修改

**修改订单状态：**
```http
PATCH /api/order/123
{
  "status": "completed"  # 修改为已完成
}
```

**回退状态：**
```http
PATCH /api/order/123
{
  "status": "pending"  # 从已完成回退到待支付
}
```

## 利用技术

### 价格操作

**负数价格：**
```json
{
  "product_id": 123,
  "price": -100.00,
  "quantity": 1
}
```

**修改前端价格：**
```javascript
// 前端代码
const price = 100.00;

// 修改为
const price = 0.01;
```

**API价格修改：**
```http
POST /api/checkout
{
  "items": [
    {
      "product_id": 123,
      "price": 0.01,  # 原价100.00
      "quantity": 1
    }
  ]
}
```

### 数量限制绕过

**负数数量：**
```json
{
  "product_id": 123,
  "quantity": -10  # 可能导致库存增加
}
```

**超出限制：**
```json
{
  "product_id": 123,
  "quantity": 999999  # 超出单次购买限制
}
```

### 优惠券滥用

**重复使用：**
```http
POST /api/checkout
{
  "coupon": "DISCOUNT50",
  "items": [...]
}

# 重复使用同一优惠券
```

**未激活优惠券：**
```http
POST /api/checkout
{
  "coupon": "EXPIRED_COUPON",  # 使用过期优惠券
  "items": [...]
}
```

### 提现漏洞

**负数提现：**
```json
{
  "amount": -1000.00  # 可能导致账户余额增加
}
```

**超出余额：**
```json
{
  "amount": 999999.00  # 超出账户余额
}
```

### 时间竞争

**并发购买：**
```python
import threading
import requests

def buy():
    requests.post('https://target.com/api/purchase',
                  json={'product_id': 123, 'quantity': 1})

# 限时抢购，并发请求
for i in range(100):
    threading.Thread(target=buy).start()
```

## 绕过技术

### 前端验证绕过

**直接调用API：**
- 绕过前端JavaScript验证
- 直接发送API请求

**修改请求：**
- 使用Burp Suite拦截
- 修改参数后发送

### 状态码分析

**观察响应：**
- 200 OK - 可能成功
- 400 Bad Request - 参数错误
- 403 Forbidden - 权限不足
- 500 Internal Server Error - 服务器错误

### 错误信息利用

**从错误信息获取信息：**
```
错误: "余额不足，当前余额: 100.00"
→ 可以获取账户余额信息
```

## 工具使用

### Burp Suite

**使用Repeater：**
1. 拦截业务请求
2. 修改关键参数
3. 观察响应

**使用Intruder：**
1. 标记参数
2. 使用Payload列表
3. 批量测试

### 自定义脚本

```python
import requests
import json

def test_price_manipulation():
    # 测试价格修改
    for price in [0.01, -100, 0, 999999]:
        data = {
            "product_id": 123,
            "price": price,
            "quantity": 1
        }
        response = requests.post('https://target.com/api/purchase',
                                json=data)
        print(f"Price {price}: {response.status_code}")

test_price_manipulation()
```

## 验证和报告

### 验证步骤

1. 确认可以绕过业务逻辑限制
2. 验证可以执行未授权操作
3. 评估影响（资金损失、数据篡改等）
4. 记录完整的POC

### 报告要点

- 漏洞位置和业务流程
- 可执行的未授权操作
- 完整的利用步骤和PoC
- 修复建议（服务端验证、业务规则检查等）

## 防护措施

### 推荐方案

1. **服务端验证**
   ```python
   def process_purchase(product_id, quantity, price):
       # 从数据库获取真实价格
       real_price = db.get_product_price(product_id)
       
       # 验证价格
       if price != real_price:
           raise ValueError("Price mismatch")
       
       # 验证数量
       if quantity <= 0:
           raise ValueError("Invalid quantity")
       
       # 处理购买
       process_order(product_id, quantity, real_price)
   ```

2. **状态机验证**
   ```python
   class OrderState:
       PENDING = "pending"
       PAID = "paid"
       SHIPPED = "shipped"
       COMPLETED = "completed"
       
       TRANSITIONS = {
           PENDING: [PAID],
           PAID: [SHIPPED],
           SHIPPED: [COMPLETED]
       }
       
       def can_transition(self, from_state, to_state):
           return to_state in self.TRANSITIONS.get(from_state, [])
   ```

3. **并发控制**
   ```python
   import threading
   
   lock = threading.Lock()
   
   def process_order(order_id):
       with lock:
           # 检查订单状态
           order = db.get_order(order_id)
           if order.status != 'pending':
               raise ValueError("Order already processed")
           
           # 处理订单
           process(order)
   ```

4. **业务规则验证**
   ```python
   def validate_business_rules(order):
       # 验证数量限制
       if order.quantity > MAX_QUANTITY:
           raise ValueError("Quantity exceeds limit")
       
       # 验证价格范围
       if order.price <= 0:
           raise ValueError("Invalid price")
       
       # 验证库存
       if order.quantity > get_stock(order.product_id):
           raise ValueError("Insufficient stock")
   ```

5. **审计日志**
   ```python
   def log_business_action(user_id, action, details):
       log_entry = {
           "user_id": user_id,
           "action": action,
           "details": details,
           "timestamp": datetime.now()
       }
       db.log_action(log_entry)
   ```

## 注意事项

- 仅在授权测试环境中进行
- 避免对业务造成实际影响
- 注意不同业务流程的差异
- 测试时注意数据一致性

## Validation & Reporting

- Confirm every finding with reproducible PoC before reporting
- Document: severity (CVSS), affected asset, steps, evidence, remediation
- Use `record_vulnerability` when running inside the penkit51 platform
- Chain low-severity findings into higher-impact attack paths
- Never report without evidence — distinguish hypothesis from confirmed vuln

