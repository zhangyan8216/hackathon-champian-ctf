# 超级CTF Agent - 集成指南

## 📌 概述

集成的超级CTF Agent v2.0 现已完全整合到现有的 `/home/ctf_agent/` 项目中！

**位置**: `/home/ctf_agent/core/super_agent.py`

## ✨ 新增功能

### 1. 多Agent架构
- **PlannerAgent** - 智能任务规划
- **ExecutorAgent** - 任务执行引擎（带缓存）
- **KnowledgeAgent** - 持久化知识库
- **MonitorAgent** - 实时监控和统计

### 2. 增强能力

#### Crypto类
- ✓ Base64自动解码
- ✓ Hex自动解码
- ✓ ROT13自动解码
- ✓ XOR暴力破解
- ✓ 熵分析
- ✓ 自动尝试所有编码方式

#### Web类
- ✓ SQL注入检测
- ✓ XSS载荷生成
- ✓ SSRF利用
- ✓ XXE攻击

#### Pwn类
- ✓ checksec安全检查
- ✓ GDB调试
- ✓ objdump分析
- ✓ pwntools利用
- ✓ angr符号执行
- ✓ 内核利用

#### Reverse类
- ✓ Ghidra反汇编
- ✓ IDA Pro集成
- ✓ 字符串提取
- ✓ 反调试绕过

#### Forensics类
- ✓ Volatility内存分析
- ✓ Binwalk文件提取
- ✓ Wireshark网络分析
- ✓ Steganography隐写术
- ✓ DNS记录提取

### 3. 智能特性

#### 学习系统
```python
# 自动保存成功经验
agent.knowledge.add(
    problem=challenge,
    solution=result,
    success=True,
    tools=used_tools
)
```

#### 知识检索
```python
# 搜索相似问题
similar = agent.knowledge.search(
    query=description,
    category="crypto"
)
```

#### 性能监控
```python
# 获取实时统计
stats = agent.get_stats()
# {
#   "monitor": {
#     "total_solved": 1,
#     "success_rate": 100.0,
#     "avg_time": 0.01,
#     "categories": {...},
#     "tools_used": {...}
#   },
#   "knowledge": 1,
#   "cache_size": 1
# }
```

## 🚀 使用方法

### 基础使用

```python
from core.super_agent import SuperCTFAgent
import asyncio

# 初始化Agent
agent = SuperCTFAgent()

# 解题
challenge = {
    "name": "My Challenge",
    "description": "Decode: SGVsbG8gQ1RGe30",
    "category": "crypto",
    "difficulty": 1,
    "data": "SGVsbG8gQ1RGe30="
}

result = asyncio.run(agent.solve_challenge(challenge))
```

### 从main.py调用

修改 `/home/ctf_agent/main.py`:

```python
from core.super_agent import SuperCTFAgent

async def solve_challenge(challenge_path):
    agent = SuperCTFAgent(config)
    
    # 读取题目
    challenge = load_challenge(challenge_path)
    
    # 解题
    result = await agent.solve_challenge(challenge)
    
    return result
```

### 命令行使用

```bash
cd /home/ctf_agent

# 解题（使用默认测试题）
python3 core/super_agent.py

# 解题（传入JSON数据）
python3 core/super_agent.py -c '{"name":"Test","description":"Decode test","category":"crypto","difficulty":1,"files":[],"data":"SGVsbG8gQ1RGe30="}'
```

## 📊 监控仪表板

可以使用之前创建的HTML仪表板 `/super_agent_dashboard.html` 来监控Agent的实时性能。

### 启动监控服务

```python
from core.super_agent import SuperCTFAgent
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

agent = SuperCTFAgent()

class DashboardAPI(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/stats':
            stats = agent.get_stats()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode())
        else:
            self.send_response(404)
            self.end_headers()

# 启动API服务器
server = HTTPServer(('localhost', 8080), DashboardAPI)
print("监控API已在 http://localhost:8080 启动")
server.serve_forever()
```

然后在仪表板中更新API端点即可。

## 🔧 配置选项

### 指定知识库文件

```python
agent = SuperCTFAgent(
    memory_file="/path/to/custom/knowledge.json"
)
```

### 使用配置文件

```python
from config import Config

config = Config.load("config.yaml")
agent = SuperCTFAgent(config=config)
```

## 📈 性能指标

Agent会自动跟踪以下指标：

- **解题总数** solved / failed
- **成功率** success_rate (%)
- **平均时间** avg_time (秒)
- **按类别统计** categories
- **工具使用** tools_used

### 获取指标

```python
stats = agent.monitor.get_metrics()
print(f"成功率: {stats['success_rate']}%")
print(f"平均用时: {stats['avg_time']}秒")
print(f"最常用工具: {max(stats['tools_used'].items(), key=lambda x: x[1])}")
```

## 🔬 高级用法

### 自定义解题策略

```python
from core.super_agent import PlannerAgent, Task

class MyPlanner(PlannerAgent):
    def _plan_crypto(self, challenge):
        tasks = super()._plan_crypto(challenge)
        
        # 添加自定义任务
        tasks.append(Task(
            action='analyze',
            tool='my_custom_tool',
            priority=10
        ))
        
        return tasks

agent = SuperCTFAgent()
agent.planner = MyPlanner()
```

### 自定义解码方法

```python
from core.super_agent import ExecutorAgent

class MyExecutor(ExecutorAgent):
    async def _decode(self, tool, challenge):
        if tool == 'my_custom_decode':
            return self._my_decode_method(challenge)
        return await super()._decode(tool, challenge)
    
    def _my_decode_method(self, challenge):
        data = challenge.get('data', '')
        # 你的解码逻辑
        return {"status": "success", "result": decoded_data}

agent = SuperCTFAgent()
agent.executor = MyExecutor()
```

## 🐛 调试技巧

### 启用详细日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)

agent = SuperCTFAgent()
```

### 查看任务列表

```python
tasks = agent.planner.plan(challenge)
for task in tasks:
    print(f"{task.action} - {task.tool} (优先级: {task.priority})")
```

### 检查知识库

```python
# 搜索知识
results = agent.knowledge.search("base64 decode", category="crypto")
for r in results:
    print(f"问题: {r['problem']['name']}")
    print(f"成功率: {r['success']}")
    print(f"访问次数: {r['access_count']}")
```

## 📚 集成示例

### 集成到现有路由

```python
# 在web_dashboard.py中
from core.super_agent import SuperCTFAgent

@app.route('/solve', methods=['POST'])
def solve():
    data = request.json
    challenge = {
        'name': data['name'],
        'description': data['description'],
        'category': data['category'],
        'difficulty': data.get('difficulty', 5),
        'files': data.get('files', []),
        'data': data.get('data')
    }
    
    agent = SuperCTFAgent()
    result = asyncio.run(agent.solve_challenge(challenge))
    
    return jsonify(result)
```

## 🎯 与原版Agent的兼容性

超级Agent完全兼容原有的CTF Agent功能：

- 保留原有的Config和Memory管理
- 可以与现有的CTFd客户端混合使用
- 支持原有的baseline基准测试

### 使用原有Agent作为备选

```python
from core.agent import CTFAgent as BaseAgent
from core.super_agent import SuperCTFAgent

class HybridAgent:
    def __init__(self):
        self.super = SuperCTFAgent()
        self.base = BaseAgent(config)
    
    async def solve(self, challenge):
        # 先尝试超级Agent
        result = await self.super.solve_challenge(challenge)
        
        # 如果失败，退回基础Agent
        if result.get('success_count', 0) == 0:
            result = await self.base.solve(challenge)
        
        return result
```

## 🔗 相关文件

```
/home/ctf_agent/
├── core/
│   ├── super_agent.py          ← 超级Agent（新增）
│   ├── agent.py                ← 原有Agent
│   ├── planner.py              ← 原有Planner
│   ├── executor.py             ← 原有Executor
│   └── memory.py               ← 原有Memory
├── main.py                     ← 主入口
├── config.yaml                 ← 配置文件
└── memory/
    └── knowledge_base.json      ← 知识库（自动生成）
```

## 📝 下一步

现在可以进行**第3个任务**: 继续增强某个特定能力！

建议优化的方向：
1. **增强解码能力** - 添加更多编码格式（Base32, Base58, Unicode等）
2. **改进漏洞利用** - 集成更多exploit工具
3. **优化知识检索** - 使用向量检索提高相似度匹配精度
4. **添加实时学习** - 实时调整策略权重

---

**Created**: 2026-02-26  
**Status**: ✅ 集成完成，测试通过
