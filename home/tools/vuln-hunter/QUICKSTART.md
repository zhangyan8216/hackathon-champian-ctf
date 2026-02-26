# 🚀 VulnHunter Enterprise - 快速开始指南

## 📋 目录
- [安装指南](#安装指南)
- [快速启动](#快速启动)
- [核心功能演示](#核心功能演示)
- [配置说明](#配置说明)
- [常见问题](#常见问题)

---

## 🛠️ 安装指南

### 系统要求
- Python 3.8+
- Linux / macOS / Windows
- 1GB+ 可用磁盘空间

### 步骤1: 克隆项目
```bash
cd /home/tools/vuln-hunter
```

### 步骤2: 创建虚拟环境（推荐）
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 步骤3: 安装依赖
```bash
# 安装所有依赖
pip install -r requirements.txt

# 如果需要PDF报告功能
pip install weasyprint openpyxl

# 如果只需要核心功能
pip install flask requests aiohttp pyyaml jinja2
```

### 步骤4: 验证安装
```bash
python3 -c "import flask, requests, aiohttp; print('✅ 依赖安装成功')"
```

---

## 🚀 快速启动

### 方式1: Web Dashboard（推荐）

#### 启动Web服务器
```bash
python3 run.py --web
```

#### 访问Dashboard
打开浏览器访问: http://localhost:5001

#### 功能：
- 📊 实时扫描监控
- 📈 漏洞统计图表
- 📄 在线报告查看
- 🔍 历史记录查询

### 方式2: 命令行扫描

#### 基础Web扫描
```bash
python3 run.py --target https://example.com
```

#### 完整扫描（包含所有检测）
```bash
python3 run.py --target https://example.com --full-scan
```

#### 扫描选项
```bash
python3 run.py \
  --target https://example.com \
  --scan-type web \
  --depth 3 \
  --threads 10 \
  --output results.json
```

#### 可用选项：
```
--target URL          目标URL或IP
--scan-type TYPE      扫描类型 (web, network, port, all)
--depth N             扫描深度 (默认: 2)
--threads N           并发线程数 (默认: 5)
--output FILE         输出文件路径
--format FORMAT       报告格式 (json, html, ascii)
--enable-ai           启用AI智能分析
```

---

## 🎯 核心功能演示

### 1. Web漏洞扫描

#### SQL注入检测
```bash
python3 run.py --target http://testphp.vulnweb.com --scan-type web
```

输出：
```
[INFO] 开始扫描: http://testphp.vulnweb.com
[INFO] 检测到 SQL 注入漏洞
       URL: http://testphp.vulnweb.com/listproducts.php?cat=1'
       类型: Error-Based SQLi
       严重程度: HIGH
```

#### XSS检测
```bash
python3 run.py --target http://testphp.vulnweb.com/artists.php?artist=1
```

#### SSRF检测
```bash
python3 -c "
from discovery import SSRFDetector
detector = SSRFDetector()
result = detector.detect('http://target.com/api?url=http://127.0.0.1/admin')
print(result)
"
```

### 2. 网络端口扫描

```bash
python3 run.py --target 192.168.1.0/24 --scan-type port
```

输出：
```
[INFO] 扫描网段: 192.168.1.0/24
[+] 192.168.1.1:22   SSH
[+] 192.168.1.100:80 HTTP
[+] 192.168.1.100:443 HTTPS
```

### 3. 目录暴破

```python
from core.scanner import WebScanner

scanner = WebScanner("https://example.com")
directories = scanner.discover_directories(
    wordlist="/path/to/wordlist.txt",
    threads=10
)

for d in directories:
    print(f"[+] {d}")
```

### 4. 自动化利用

```bash
python3 AUTO_EXPLOITER.py --target http://vulnerable-site.com
```

功能：
- 检测漏洞
- 自动尝试利用
- 生成利用链

### 5. AI智能分析

```bash
python3 AI_ENHANCEMENT.py --report scan_results.json
```

功能：
- 自动评估漏洞风险
- 生成修复建议
- 优先级排序

### 6. 专业报告生成

```bash
python3 PROFESSIONAL_REPORT.py --input scan_results.json --output report.html --format html
```

输出：
- HTML报告（带图表）
- PDF报告（可选）
- Excel报告（可选）

---

## ⚙️ 配置说明

### 配置文件位置
```
/home/tools/vuln-hunter/config/config.yaml
```

### 配置示例

```yaml
# 扫描配置
scanner:
  timeout: 10
  max_depth: 3
  threads: 5
  user_agent: "VulnHunter/1.0"

# 漏洞检测
detector:
  check_sqli: true
  check_xss: true
  check_ssrf: true
  check_xxe: true

# 报告配置
reporter:
  output_dir: "./reports"
  formats: ["json", "html", "ascii"]
  include_screenshots: false

# AI配置
ai:
  enabled: true
  model: "gpt-3.5-turbo"
  api_key: "your-api-key"

# 工具集成
tools:
  sqlmap_path: "/usr/bin/sqlmap"
  nmap_path: "/usr/bin/nmap"
```

### 环境变量

```bash
# API密钥
export VULNHUNTER_API_KEY="your-api-key"

# 代理设置
export HTTP_PROXY="http://proxy:8080"
export HTTPS_PROXY="http://proxy:8080"

# 日志级别
export LOG_LEVEL="DEBUG"
```

---

## 🧪 测试

### 运行测试套件
```bash
# 安装测试依赖
pip install pytest pytest-asyncio pytest-cov

# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_scanner.py -v

# 生成覆盖率报告
pytest --cov=. --cov-report=html
```

### 示例测试
```python
# tests/test_scanner.py
import pytest
from core.scanner import WebScanner

def test_web_scanner_init():
    scanner = WebScanner("https://example.com")
    assert scanner.url == "https://example.com"

def test_directory_discovery():
    scanner = WebScanner("https://example.com")
    # 测试目录发现功能
    pass
```

---

## 📊 使用场景

### 场景1: 渗透测试
```bash
# 完整渗透测试流程
python3 run.py --target https://target.com --full-scan --enable-ai

# 查看 Dashboard
open http://localhost:5001

# 生成报告
python3 PROFESSIONAL_REPORT.py --input results.json --output penetration_test_report.html
```

### 场景2: 漏洞评估
```bash
# 快速扫描
python3 run.py --target https://app.example.com --scan-type web

# AI分析
python3 AI_ENHANCEMENT.py --report results.json

# 导出报告
python3 PROFESSIONAL_REPORT.py --input results.json --output vulnerability_assessment.pdf
```

### 场景3: 持续监控
```bash
# 启动Web服务
python3 run.py --web --monitor-mode

# 定期扫描（Cron）
*/30 * * * * cd /home/tools/vuln-hunter && python3 run.py --target https://app.com --output cron_scan.json
```

---

## ❓ 常见问题

### Q1: 安装pandas失败？
```bash
# 使用清华源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pandas
```

### Q2: 扫描速度慢？
调整并发数：
```yaml
# config.yaml
scanner:
  threads: 20  # 增加线程数
  timeout: 5   # 减少超时时间
```

### Q3: 如何绕过WAF？
修改User-Agent和Header：
```python
headers = {
    'User-Agent': 'Mozilla/5.0',
    'X-Forwarded-For': '127.0.0.1'
}
scanner = WebScanner(url, headers=headers)
```

### Q4: 如何自定义Payload？
```python
from detection import SQLiDetector

detector = SQLiDetector()
detector.custom_payloads = [
    "' OR '1'='1",
    "admin'--",
    "' UNION SELECT * FROM users--"
]
```

### Q5: 报告生成失败？
```bash
# 安装PDF依赖
pip install weasyprint

# 或只生成HTML报告
python3 PROFESSIONAL_REPORT.py --format html
```

---

## 🔧 高级用法

### 1. 自定义检测模块
```python
from detection import BaseDetector

class CustomDetector(BaseDetector):
    def detect(self, response):
        # 自定义检测逻辑
        if "vulnerability" in response.text:
            return {
                "type": "Custom",
                "severity": "HIGH",
                "details": "Custom vulnerability detected"
            }
        return None
```

### 2. 集成外部工具
```python
import subprocess

def run_sqlmap(url):
    result = subprocess.run(
        ["sqlmap", "-u", url, "--batch"],
        capture_output=True,
        text=True
    )
    return result.stdout
```

### 3. 集群扫描
```bash
# 使用GNU Parallel
cat targets.txt | parallel -j 10 "python3 run.py --target {} --output results_{}.json"
```

---

## 📚 更多资源

- [完整文档](README.md)
- [API文档](docs/API.md)
- [配置说明](config/config.yaml)
- [报告示例](examples/)

---

## 💡 提示

- ⚡ 使用`--threads`参数提高扫描速度
- 🔒 扫描前确保有授权
- 📝 定期生成报告进行对比
- 🤖 启用AI功能可获得更智能的分析

---

**祝使用愉快！如有问题，请查看[GitHub Issues](https://github.com/your-org/vulnhunter/issues)**
