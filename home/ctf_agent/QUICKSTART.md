# 🎯 CTF Agent - 快速开始指南

## 📋 目录
- [安装指南](#安装指南)
- [快速启动](#快速启动)
- [核心功能演示](#核心功能演示)
- [配置说明](#配置说明)
- [使用技巧](#使用技巧)
- [常见问题](#常见问题)

---

## 🛠️ 安装指南

### 系统要求
- Python 3.10+
- Docker (可选，用于沙箱隔离)
- 2GB+ 可用磁盘空间
- 推荐内存: 4GB+

### 步骤1: 进入项目目录
```bash
cd /home/ctf_agent
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

# 如果使用Docker功能
pip install -r requirements.txt
# 确保Docker已安装并运行
docker --version
```

### 步骤4: 配置LLM API
```bash
# 复制配置模板
cp config.yaml.example config.yaml

# 编辑 config.yaml 或使用环境变量
export ANTHROPIC_API_KEY="your-key-here"
# 或
export OPENAI_API_KEY="your-key-here"
```

### 步骤5: 验证安装
```bash
python3 -c "import anthropic, openai, docker; print('✅ 依赖安装成功')"
python3 main.py --validate-config
```

---

## 🚀 快速启动

### 方式1: 交互模式（推荐）

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动交互模式
python3 main.py
```

交互模式示例：
```
🎮 CTF Agent - 交互模式
选择题型:
  1. Crypto (密码学)
  2. Web (Web安全)
  3. Pwn (二进制利用)
  4. Forensics (数字取证)
  5. Reverse (逆向工程)

> 1

🔐 Crypto题目
输入题目描述: 
这道题给了一串base64编码: SGVsbG8gQ1RG

输入提示（可选）: 

正在思考...

✅ 解题成功！
Flag: Hello CTF
方法: base64_decode
```

### 方式2: 单题模式

```bash
# 解单个题目
python3 main.py --challenge /path/to/challenge --type crypto

# 查看帮助
python3 main.py --help
```

### 方式3: 自动模式（CTFd集成）

适用于CTFd平台的自动化：

```bash
# 配置.env文件
cat > .env << EOF
CTFD_BASE_URL=https://ctf.example.com
CTFD_TOKEN=your-access-token
OPENAI_API_KEY=your-key-here
EOF

# 运行自动解题
python3 main.py --auto
```

Agent会自动：
1. 获取所有未解题目
2. 逐个解题
3. 提交flag
4. 记录解题过程

### 方式4: Docker沙箱模式（安全）

```bash
# 构建Docker镜像
docker build -t ctf-tools:latest -f sandbox/Dockerfile .

# 运行沙箱
docker run -it --rm \
  -v $(pwd):/workspace \
  ctf-tools:latest \
  python3 main.py
```

---

## 🎯 核心功能演示

### 1. 密码学工具

#### Base64解码
```python
from tools.enhanced_tools import base64_decode

result = base64_decode("SGVsbG8gQ1RG")
print(result)  # Hello CTF
```

#### XOR暴力破解
```python
from tools.enhanced_tools import xor_bruteforce

encrypted = "\x1f\x1e\x1d\x1c"
result = xor_bruteforce(encrypted)
print(result)  # 自动找到正确的密钥和明文
```

#### 凯撒密码
```python
from tools.enhanced_tools import caesar_decrypt

ciphertext = "Khoor Zruog"
plaintext = caesar_decrypt(ciphertext)
print(plaintext)  # Hello World
```

### 2. Web安全工具

#### SQL注入检测
```python
from tools.enhanced_tools import check_sqli

url = "http://example.com/page?id=1"
result = check_sqli(url)
print(result)  # 返回潜在的注入点
```

#### XSS检测
```python
from tools.enhanced_tools import check_xss

payload = "<script>alert(1)</script>"
result = check_xss(payload)
print(result)  # 检测XSS载荷
```

### 3. 隐写术工具

#### 字符串提取
```python
from tools.enhanced_tools import extract_strings

strings = extract_strings("/path/to/binary")
print(strings[:10])  # 前10个字符串
```

#### 文件类型检测
```python
from tools.enhanced_tools import detect_filetype

filetype = detect_filetype("/path/to/unknown_file")
print(filetype)  # 文件类型信息
```

### 4. 编码解码

#### 自动解码
```python
from tools.enhanced_tools import auto_decode

encoded_data = "SGVsbG8="
result = auto_decode(encoded_data, attempts=['base64', 'hex', 'rot13'])
print(result)  # 自动尝试多种编码
```

#### URL解码
```python
from tools.enhanced_tools import url_decode

encoded = "Hello%20World"
decoded = url_decode(encoded)
print(decoded)  # Hello World
```

### 5. ReAct推理循环

```python
from core.agent import CTFAgent
from config import Config

# 初始化配置
config = Config()

# 创建Agent
agent = CTFAgent(config)

# 运行ReAct循环
problem = {
    "description": "一串base64编码: SGVsbG8gQ1RG",
    "type": "crypto"
}

solution = agent.solve(problem)
print(solution)
```

输出：
```
思考：题目描述提到base64编码，我应该使用base64_decode工具

行动：调用工具 base64_decode("SGVsbG8gQ1RG")

观察：得到结果 "Hello CTF"

思考：看起来像flag，格式正确，应该就是答案

最终答案：Hello CTF
```

---

## ⚙️ 配置说明

### 配置文件: config.yaml

```yaml
# LLM配置
llm:
  provider: anthropic  # 或 openai
  model: claude-3-sonnet-20240229  # 或 gpt-4
  api_key: ${ANTHROPIC_API_KEY}  # 从环境变量读取
  temperature: 0.3
  max_tokens: 2000

# 解题配置
solver:
  max_iterations: 10  # 最大尝试次数
  timeout: 120  # 单步超时(秒)
  parallel_attempts: 3  # 并发尝试数

# 工具配置
tools:
  enable_crypto: true
  enable_web: true
  enable_forensics: true
  enable_pwn: false  # 需要pwntools
  
# Docker配置（可选）
docker:
  enabled: false  # 是否启用沙箱
  image: ctf-tools:latest
  timeout: 300

# 日志配置
logging:
  level: INFO
  file: logs/agent.log
  max_size: 10MB
  backup_count: 5

# CTFd配置
ctfd:
  base_url: ${CTFD_BASE_URL}
  token: ${CTFD_TOKEN}
  auto_submit: true
  retry_on_fail: true

# 性能优化
performance:
  cache_tool_results: true
  cache_ttl: 3600
  use_async: true
```

### 环境变量

```bash
# LLM API密钥
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."

# CTFd配置
export CTFD_BASE_URL="https://ctf.example.com"
export CTFD_TOKEN="your-access-token"

# Docker配置
export DOCKER_HOST="unix:///var/run/docker.sock"

# 日志级别
export LOG_LEVEL="DEBUG"
```

---

## 📚 使用技巧

### 技巧1: 批量解题

```python
# 批量处理多个题目
import os
from core.agent import CTFAgent
from config import Config

challenges = [
    {"file": "challenge1.txt", "type": "crypto"},
    {"file": "challenge2.txt", "type": "web"},
    {"file": "challenge3.txt", "type": "forensics"}
]

agent = CTFAgent(Config())
results = []

for challenge in challenges:
    with open(challenge['file']) as f:
        description = f.read()
    
    result = agent.solve({
        "description": description,
        "type": challenge['type']
    })
    
    results.append(result)
    print(f"{challenge['file']}: {result['flag']}")

# 保存结果
import json
with open("results.json", "w") as f:
    json.dump(results, f, indent=2)
```

### 技巧2: 自定义工具

```python
from tools.toolkit import ToolRegistry
from tools.base_tool import BaseTool

class MyCustomTool(BaseTool):
    """自定义工具"""
    
    name = "my_tool"
    description = "我的自定义工具"
    
    def execute(self, args):
        # 实现工具逻辑
        input_data = args.get("input", "")
        result = self.process(input_data)
        return result
    
    def process(self, data):
        # 处理逻辑
        return f"Processed: {data}"

# 注册工具
registry = ToolRegistry()
registry.register(MyCustomTool())

# 使用工具
result = registry.execute("my_tool", {"input": "test"})
print(result)
```

### 技巧3: 知识库扩展

```python
from knowledge.rag import KnowledgeBase

# 添加自定义知识
kb = KnowledgeBase()
kb.add_entry({
    "category": "custom",
    "problem": "如何解决特定问题",
    "solution": "解决方案描述",
    "code": "相关代码示例"
})

# 搜索知识
results = kb.search("特定问题")
for result in results:
    print(result['solution'])
```

### 技巧4: 性能优化

```yaml
# config.yaml
performance:
  # 启用结果缓存
  cache_tool_results: true
  
  # 使用异步执行
  use_async: true
  
  # 限制并发数
  max_concurrent: 5
  
  # 减少LLM调用
  use_cache_for_llm: true
```

### 技巧5: 调试模式

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# 或在代码中设置
from core.agent import CTFAgent
import logging

agent = CTFAgent(Config())
agent.logger.setLevel(logging.DEBUG)

# 详细日志会显示：
# - 工具调用
# - LLM推理过程
# - 中间结果
```

---

## 🧪 测试

### 运行测试套件
```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_crypto.py -v

# 生成覆盖率报告
pytest --cov=. --cov-report=html

# 查看覆盖率
open htmlcov/index.html
```

### 编写测试示例

```python
# tests/test_crypto.py
import pytest
from tools.enhanced_tools import base64_decode

def test_base64_decode():
    """测试Base64解码"""
    assert base64_decode("SGVsbG8=") == "Hello"
    assert base64_decode("") is None
    
def test_xor_bruteforce():
    """测试XOR暴力破解"""
    encrypted = b"\x1f\x1e\x1d\x1c"
    result = xor_bruteforce(encrypted)
    assert result is not None
```

---

## ❓ 常见问题

### Q1: API密钥在哪里配置？
```bash
# 方式1: 环境变量（推荐）
export ANTHROPIC_API_KEY="your-key"

# 方式2: config.yaml文件
llm:
  api_key: sk-antic-xxx

# 方式3: .env文件
echo "ANTHROPIC_API_KEY=sk-anti-xxx" > .env
```

### Q2: 如何降低使用成本？
```yaml
# 使用更便宜的模型
llm:
  model: claude-3-haiku  # 比sonnet便宜

# 减少max_tokens
llm:
  max_tokens: 1000

# 启用缓存
performance:
  cache_tool_results: true
```

### Q3: 解题速度慢？
```yaml
# 减少迭代次数
solver:
  max_iterations: 5

# 启用异步
performance:
  use_async: true
  max_concurrent: 10
```

### Q4: Docker沙箱启动失败？
```bash
# 检查Docker是否运行
docker ps

# 重新构建镜像
docker build -t ctf-tools:latest -f sandbox/Dockerfile .

# 查看日志
docker logs ctf-tools
```

### Q5: 如何添加新工具？
```python
# 1. 在tools/目录创建新文件
# tools/my_new_tool.py

from tools.base_tool import BaseTool

class MyNewTool(BaseTool):
    name = "my_new_tool"
    description = "描述工具功能"
    
    def execute(self, args):
        # 实现逻辑
        return result

# 2. 在core/agent.py中注册
from tools.my_new_tool import MyNewTool
self.tool_registry.register(MyNewTool())
```

---

## 🎯 典型工作流程

```
1. 获取题目
   ↓
2. 分析题目类型
   ↓
3. ReAct推理
   - 思考：判断需要什么工具
   - 行动：调用工具
   - 观察：获取结果
   ↓
4. 评估结果
   - 是否得到flag？
   - 是否需要继续？
   ↓
5. 提交flag
   ↓
6. 记录知识
   - 保存解题过程
   - 更新记忆
   ↓
7. 下一题
```

---

## 📊 CLI工具

### 记忆管理
```bash
python src/cli_cli.py memory show              # 查看已解决的题目
python src/cli_cli.py memory clear             # 清空记忆
python src/cli_cli.py memory show_challenge 1  # 查看特定题目记忆
```

### 知识库搜索
```bash
python src/cli_cli.py knowledge search crypto XOR    # 搜索知识
python src/cli_cli.py knowledge add                 # 添加知识条目
```

### 工具测试
```bash
python src/cli_cli.py tools test base64_decode     # 测试工具
python src/cli_cli.py tools list                   # 列出所有工具
```

---

## 📚 更多资源

- [完整文档](README.md)
- [架构设计](docs/ARCHITECTURE.md)
- [API文档](docs/API.md)
- [示例代码](examples/)
- [贡献指南](CONTRIBUTING.md)

---

## 💡 最佳实践

1. **先手动分析**在交给Agent前，先快速扫描题目
2. **合理配置**根据题目难度调整max_iterations
3. **善用缓存**启用缓存可以节省成本和时间
4. **记录经验**使用记忆功能积累解题经验
5. **组合使用**手动+自动结合效果最好

---

**祝解题愉快！Flag Get! 🚩**
