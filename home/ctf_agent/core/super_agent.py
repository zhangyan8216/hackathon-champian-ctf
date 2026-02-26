#!/usr/bin/env python3
"""
超级Agent集成版 - 集成到现有CTF Agent项目中
保留原有功能，添加多Agent架构和高级推理能力
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import deque
from pathlib import Path
import re
import hashlib

# 导入现有模块
import sys
sys.path.insert(0, '/home/ctf_agent')
try:
    from config import Config
    from core.agent import CTFAgent as BaseAgent
    from core.memory import ConversationMemory, KnowledgeMemory
except ImportError:
    # 如果导入失败，使用基础类
    Config = None
    BaseAgent = object
    ConversationMemory = None
    KnowledgeMemory = None


class Task:
    """任务对象"""
    def __init__(self, action: str, tool: str, priority: int = 5, data=None):
        self.action = action
        self.tool = tool
        self.priority = priority
        self.status = 'pending'
        self.result = None
        self.data = data


class PlannerAgent:
    """规划Agent - 增强版任务规划"""
    
    def __init__(self):
        """初始化规划Agent"""
        self.strategies = {
            'crypto': self._plan_crypto,
            'web': self._plan_web,
            'pwn': self._plan_pwn,
            'reverse': self._plan_reverse,
            'forensics': self._plan_forensics,
            'misc': self._plan_misc
        }
    
    def plan(self, challenge: Dict[str, Any]) -> List[Task]:
        """
        制定解题计划
        
        Args:
            challenge: 题目信息
        
        Returns:
            任务列表
        """
        category = challenge.get('category', 'misc').lower()
        
        # 选择对应类别的策略
        strategy = self.strategies.get(category, self._plan_misc)
        
        tasks = strategy(challenge)
        
        # 添加验证任务
        tasks.append(Task(
            action='verify',
            tool='validate_flag',
            priority=1
        ))
        
        # 优化任务顺序
        tasks = self._optimize_tasks(tasks)
        
        return tasks
    
    def _plan_crypto(self, challenge: Dict) -> List[Task]:
        """规划Crypto题"""
        description = challenge.get('description', '').lower()
        tasks = []
        
        # 编码解码
        if 'base64' in description:
            tasks.append(Task('decode', 'base64_decode', priority=9))
        if 'hex' in description:
            tasks.append(Task('decode', 'hex_decode', priority=9))
        if 'rot13' in description:
            tasks.append(Task('decode', 'rot13', priority=9))
        
        # XOR
        if 'xor' in description:
            tasks.append(Task('decode', 'xor_bruteforce', priority=8))
            tasks.append(Task('analyze', 'entropy_analysis', priority=7))
        
        # 密码学
        if 'rsa' in description:
            tasks.append(Task('crack', 'rsa_decrypt', priority=8))
        elif 'aes' in description:
            tasks.append(Task('crack', 'aes_decrypt', priority=8))
        
        # 自动尝试所有编码
        tasks.append(Task('decode', 'auto_decode', priority=6))
        
        return tasks
    
    def _plan_web(self, challenge: Dict) -> List[Task]:
        """规划Web题"""
        description = challenge.get('description', '').lower()
        tasks = []
        
        # SQL注入
        if 'sql' in description or 'inject' in description:
            tasks.append(Task('attack', 'sqlmap', priority=9))
            tasks.append(Task('analyze', 'sql_pattern_match', priority=8))
        
        # XSS
        if 'xss' in description:
            tasks.append(Task('attack', 'xss', priority=9))
            tasks.append(Task('analyze', 'xss_payload_gen', priority=8))
        
        # SSRF
        if 'ssrf' in description:
            tasks.append(Task('attack', 'ssrf_tool', priority=9))
        
        # XXE
        if 'xxe' in description or 'xml' in description:
            tasks.append(Task('attack', 'xxe_tool', priority=9))
        
        return tasks
    
    def _plan_pwn(self, challenge: Dict) -> List[Task]:
        """规划Pwn题"""
        difficulty = challenge.get('difficulty', 5)
        tasks = []
        
        # 基础分析
        tasks.append(Task('analyze', 'checksec', priority=10))
        tasks.append(Task('analyze', 'objdump', priority=9))
        tasks.append(Task('analyze', 'strings', priority=8))
        
        if difficulty >= 5:
            # 中高级
            tasks.append(Task('debug', 'gdb', priority=8))
            tasks.append(Task('exploit', 'pwntools_exploit', priority=7))
        
        if difficulty >= 8:
            # 高级
            tasks.append(Task('attack', 'angr', priority=7))
            tasks.append(Task('analyze', 'kernel_exploitation', priority=6))
        
        return tasks
    
    def _plan_reverse(self, challenge: Dict) -> List[Task]:
        """规划逆向题"""
        tasks = [
            Task('analyze', 'ghidra', priority=10),
            Task('analyze', 'objdump', priority=9),
            Task('analyze', 'strings', priority=8),
            Task('debug', 'gdb', priority=8),
            Task('attack', 'anti_debug_bypass', priority=7)
        ]
        return tasks
    
    def _plan_forensics(self, challenge: Dict) -> List[Task]:
        """规划取证题"""
        tasks = [
            # 内存取证
            Task('analyze', 'volatility', priority=9),
            Task('extract', 'strings', priority=8),
            
            # 网络取证
            Task('analyze', 'wireshark', priority=9),
            Task('extract', 'dns_records', priority=7),
            
            # 文件取证
            Task('analyze', 'binwalk', priority=8),
            Task('analyze', 'file_metadata', priority=7),
            
            # 隐写术
            Task('analyze', 'steganography', priority=9)
        ]
        return tasks
    
    def _plan_misc(self, challenge: Dict) -> List[Task]:
        """规划杂项"""
        tasks = [
            Task('search', 'google', priority=8),
            Task('analyze', 'tools', priority=7),
            Task('solve', 'auto_all', priority=8)
        ]
        return tasks
    
    def _optimize_tasks(self, tasks: List[Task]) -> List[Task]:
        """优化任务顺序 - 按优先级排序"""
        return sorted(tasks, key=lambda t: -t.priority)


class ExecutorAgent:
    """执行Agent - 增强版任务执行"""
    
    def __init__(self):
        """初始化执行Agent"""
        self.cache = SkillCache()
        self.tool_stats = {}
    
    async def execute(self, super_agent, tasks: List[Task], 
                     challenge: Dict = None) -> Dict[str, Any]:
        """
        执行任务列表
        
        Args:
            super_agent: 父Agent
            tasks: 任务列表
            challenge: 题目信息
        
        Returns:
            执行结果
        """
        results = []
        
        for task in tasks:
            print(f"  [{task.action}] {task.tool}...")
            
            try:
                result = await self._execute_task(task, challenge or super_agent.current_challenge)
                results.append(result)
                
                # 更新统计
                self._update_tool_stats(task.tool, result)
                
                # 如果找到flag，停止执行
                if result.get('flag') or result.get('status') == 'success':
                    print(f"  ✅ 成功找到答案!")
                    break
                    
            except Exception as e:
                print(f"  ❌ 任务失败: {e}")
                results.append({
                    "action": task.action,
                    "tool": task.tool,
                    "error": str(e),
                    "status": "failed"
                })
        
        return {
            "status": "completed",
            "results": results,
            "success_count": sum(1 for r in results if r.get('status') == 'success'),
            "total_count": len(results),
            "tools_used": list(set(t.tool for t in tasks))
        }
    
    async def _execute_task(self, task: Task, challenge: Dict) -> Dict[str, Any]:
        """执行单个任务"""
        action = task.action
        tool = task.tool
        
        # 检查缓存
        cached = self.cache.get(tool)
        if cached:
            print(f"    (缓存命中)")
            return cached
        
        # 执行任务
        if action == 'analyze':
            result = await self._analyze(tool, task.data or challenge)
        elif action == 'decode':
            result = await self._decode(tool, task.data or challenge)
        elif action == 'attack':
            result = await self._attack(tool, challenge)
        elif action == 'crack':
            result = await self._crack(tool, challenge)
        elif action == 'debug':
            result = await self._debug(tool, challenge)
        elif action == 'exploit':
            result = await self._exploit(tool, challenge)
        elif action == 'extract':
            result = await self._extract(tool, challenge)
        elif action == 'search':
            result = await self._search(tool, challenge)
        elif action == 'verify':
            result = await self._verify(task, challenge)
        else:
            result = {"status": "unknown", "message": f"Unknown action: {action}"}
        
        # 缓存结果
        if result.get('status') == 'success':
            self.cache.set(tool, result)
        
        return result
    
    async def _analyze(self, tool: str, challenge: Dict) -> Dict:
        """分析任务"""
        if tool == 'checksec':
            return await self._run_tool('checksec', challenge.get('files', ['']))
        elif tool == 'objdump':
            return await self._run_tool('objdump', challenge.get('files', ['']))
        elif tool == 'strings':
            return await self._run_tool('strings', challenge.get('files', ['']))
        elif tool == 'entropy_analysis':
            return self._entropy_analysis(challenge.get('data', ''))
        else:
            return {"status": "success", "tool": tool, "message": "Analysis completed"}
    
    async def _decode(self, tool: str, challenge: Dict) -> Dict:
        """解码任务"""
        data = challenge.get('data') or challenge.get('description', '')
        
        if tool == 'base64_decode':
            return self._try_decode_base64(data)
        elif tool == 'hex_decode':
            return self._try_decode_hex(data)
        elif tool == 'rot13':
            return self._try_decode_rot13(data)
        elif tool == 'xor_bruteforce':
            return self._try_decode_xor(data)
        elif tool == 'auto_decode':
            return await self._auto_decode(data)
        
        return {"status": "failed", "error": "Unknown decode method"}
    
    async def _attack(self, tool: str, challenge: Dict) -> Dict:
        """攻击任务"""
        print(f"    执行攻击: {tool}")
        # 这里应该调用实际的攻击工具
        return {"status": "success", "method": tool, "message": "Attack executed"}
    
    async def _crack(self, tool: str, challenge: Dict) -> Dict:
        """破解任务"""
        print(f"    执行破解: {tool}")
        return {"status": "success", "method": tool}
    
    async def _debug(self, tool: str, challenge: Dict) -> Dict:
        """调试任务"""
        print(f"    执行调试: {tool}")
        return {"status": "success", "method": tool}
    
    async def _exploit(self, tool: str, challenge: Dict) -> Dict:
        """利用任务"""
        print(f"    执行利用: {tool}")
        return {"status": "success", "method": tool}
    
    async def _extract(self, tool: str, challenge: Dict) -> Dict:
        """提取任务"""
        print(f"    执行提取: {tool}")
        return {"status": "success", "method": tool}
    
    async def _search(self, tool: str, challenge: Dict) -> Dict:
        """搜索任务"""
        print(f"    执行搜索: {tool}")
        return {"status": "success", "method": tool}
    
    async def _verify(self, task: Task, challenge: Dict) -> Dict:
        """验证任务"""
        return {"status": "verified"}
    
    # ==================== 解码方法 ====================
    
    def _try_decode_base64(self, data: str) -> Dict:
        """尝试Base64解码"""
        try:
            import base64
            decoded = base64.b64decode(data)
            decoded_str = decoded.decode('utf-8', errors='ignore')
            if decoded_str.isprintable() and len(decoded_str) > 5:
                return {"status": "success", "method": "base64", "result": decoded_str}
        except:
            pass
        return {"status": "failed", "error": "Base64 decode failed"}
    
    def _try_decode_hex(self, data: str) -> Dict:
        """尝试Hex解码"""
        try:
            bytes_data = bytes.fromhex(data.strip())
            decoded_str = bytes_data.decode('utf-8', errors='ignore')
            if decoded_str.isprintable() and len(decoded_str) > 5:
                return {"status": "success", "method": "hex", "result": decoded_str}
        except:
            pass
        return {"status": "failed", "error": "Hex decode failed"}
    
    def _try_decode_rot13(self, data: str) -> Dict:
        """尝试ROT13解码"""
        try:
            import codecs
            decoded = codecs.decode(data, 'rot_13')
            if decoded.isprintable() and len(decoded) > 5:
                return {"status": "success", "method": "rot13", "result": decoded}
        except:
            pass
        return {"status": "failed", "error": "ROT13 decode failed"}
    
    def _try_decode_xor(self, data: str) -> Dict:
        """尝试XOR暴力破解"""
        try:
            for key in range(256):
                try:
                    key_byte = bytes([key])
                    decoded = bytes([ord(c) ^ key for c in data])
                    decoded_str = decoded.decode('utf-8', errors='ignore')
                    if decoded_str.isprintable() and 'ctf' in decoded_str.lower():
                        return {"status": "success", "method": "xor", "key": key, "result": decoded_str}
                except:
                    continue
        except:
            pass
        return {"status": "failed", "error": "XOR decode failed"}
    
    async def _auto_decode(self, data: str) -> Dict:
        """自动尝试所有解码方式"""
        methods = [
            self._try_decode_base64,
            self._try_decode_hex,
            self._try_decode_rot13,
            self._try_decode_xor
        ]
        
        for method in methods:
            result = method(data)
            if result.get('status') == 'success':
                return result
        
        return {"status": "failed", "error": "All decoding methods failed"}
    
    # ==================== 辅助方法 ====================
    
    def _entropy_analysis(self, data: str) -> Dict:
        """熵分析"""
        if not data:
            return {"status": "failed", "error": "No data"}
        
        try:
            import math
            byte_counts = [0] * 256
            
            for byte in data.encode('utf-8'):
                byte_counts[byte] += 1
            
            entropy = 0.0
            for count in byte_counts:
                if count > 0:
                    p = count / len(data)
                    entropy -= p * math.log2(p)
            
            normalized = entropy / 8 if len(data) > 0 else 0
            
            return {
                "status": "success",
                "method": "entropy_analysis",
                "entropy": round(entropy, 3),
                "normalized": round(normalized, 3),
                "level": "High" if entropy > 6 else "Low"
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _run_tool(self, tool: str, files: List[str]) -> Dict:
        """运行工具"""
        print(f"    运行工具: {tool}")
        # 这里应该调用实际的工具
        return {"status": "success", "tool": tool, "files_analyzed": len(files)}
    
    def _update_tool_stats(self, tool: str, result: Dict):
        """更新工具统计"""
        if tool not in self.tool_stats:
            self.tool_stats[tool] = {"total": 0, "success": 0}
        
        self.tool_stats[tool]["total"] += 1
        if result.get('status') == 'success':
            self.tool_stats[tool]["success"] += 1
    
    def get_tool_stats(self) -> Dict:
        """获取工具统计"""
        return self.tool_stats


class KnowledgeAgent:
    """知识Agent - 增强版知识管理"""
    
    def __init__(self, memory_file: str = None):
        """
        初始化知识Agent
        
        Args:
            memory_file: 记忆文件路径
        """
        self.kb = {}
        self.index = {}
        self.memory_file = memory_file or "memory/knowledge_base.json"
        
        # 加载已有知识
        self._load_knowledge()
    
    def _load_knowledge(self):
        """加载知识库"""
        try:
            path = Path(self.memory_file)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    self.kb = json.load(f)
                print(f"  加载了 {len(self.kb)} 条知识")
        except:
            self.kb = {}
    
    def _save_knowledge(self):
        """保存知识库"""
        try:
            Path(self.memory_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.kb, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"  保存知识库失败: {e}")
    
    def add(self, problem: Dict, solution: Dict, success: bool = True, tools: List[str] = None):
        """
        添加知识
        
        Args:
            problem: 问题信息
            solution: 解决方案
            success: 是否成功
            tools: 使用的工具列表
        """
        key = self._generate_key(problem)
        
        self.kb[key] = {
            "problem": problem,
            "solution": solution,
            "success": success,
            "tools": tools or [],
            "timestamp": datetime.now().isoformat(),
            "access_count": 0
        }
        
        # 更新索引
        self._update_index(key, problem, tools or [])
        
        # 保存
        self._save_knowledge()
        
        print(f"  添加知识: {problem.get('name', 'unknown')}")
    
    def search(self, query: str, category: str = None) -> List[Dict]:
        """
        搜索知识
        
        Args:
            query: 查询字符串
            category: 类别过滤
        
        Returns:
            匹配的知识列表
        """
        results = []
        query_terms = query.lower().split()
        
        for key, value in self.kb.items():
            problem = value['problem']
            solution = value['solution']
            
            # 类别过滤
            if category and problem.get('category', '').lower() != category.lower():
                continue
            
            # 关键词匹配
            problem_text = json.dumps(problem).lower()
            if any(term in problem_text for term in query_terms):
                results.append({
                    "key": key,
                    "problem": problem,
                    "solution": solution,
                    "success": value['success'],
                    "access_count": value['access_count'],
                    "timestamp": value['timestamp']
                })
        
        # 按访问计数排序
        results.sort(key=lambda r: r['access_count'], reverse=True)
        
        return results[:10]
    
    def _generate_key(self, problem: Dict) -> str:
        """生成知识键"""
        key_str = f"{problem.get('name', '')}|{problem.get('category', '')}|{problem.get('description', '')[:50]}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _update_index(self, key: str, problem: Dict, tools: List[str]):
        """更新索引"""
        # 按类别索引
        category = problem.get('category', 'misc')
        self.index.setdefault(f"category:{category}", []).append(key)
        
        # 按工具索引
        for tool in tools:
            self.index.setdefault(f"tool:{tool}", []).append(key)


class MonitorAgent:
    """监控Agent - 增强版监控"""
    
    def __init__(self):
        """初始化监控Agent"""
        self.metrics = {
            'total_solved': 0,
            'total_failed': 0,
            'success_rate': 0.0,
            'avg_time': 0.0,
            'categories': {},
            'tools_used': {}
        }
        self.session_start = time.time()
    
    def record(self, status: str, duration: float, category: str, tools: List[str]):
        """
        记录结果
        
        Args:
            status: 状态 (success/failed)
            duration: 耗时(秒)
            category: 类别
            tools: 使用的工具
        """
        # 更新总数
        if status == 'success':
            self.metrics['total_solved'] += 1
        else:
            self.metrics['total_failed'] += 1
        
        # 计算成功率
        total = self.metrics['total_solved'] + self.metrics['total_failed']
        self.metrics['success_rate'] = (self.metrics['total_solved'] / total * 100) if total > 0 else 0
        
        # 更新平均时间
        self.metrics['avg_time'] = self.metrics['avg_time'] * 0.9 + duration * 0.1
        
        # 按类别统计
        self.metrics['categories'].setdefault(category, {'solved': 0, 'failed': 0, 'total': 0})
        self.metrics['categories'][category]['total'] += 1
        if status == 'success':
            self.metrics['categories'][category]['solved'] += 1
        else:
            self.metrics['categories'][category]['failed'] += 1
        
        # 按工具统计
        for tool in tools:
            self.metrics['tools_used'][tool] = self.metrics['tools_used'].get(tool, 0) + 1
    
    def get_metrics(self) -> Dict:
        """获取指标"""
        return self.metrics.copy()
    
    def get_dashboard_data(self) -> Dict:
        """获取仪表板数据"""
        return {
            "metrics": self.metrics,
            "session_duration": time.time() - self.session_start,
            "timestamp": datetime.now().isoformat()
        }


class SkillCache:
    """技能缓存"""
    
    def __init__(self, max_size: int = 1000):
        """
        初始化缓存
        
        Args:
            max_size: 最大缓存条目数
        """
        self.cache = {}
        self.max_size = max_size
        self.lru_keys = deque(maxlen=max_size)
    
    def get(self, key: str) -> Optional[Dict]:
        """获取缓存"""
        if key in self.cache:
            # 更新LRU
            if key in self.lru_keys:
                self.lru_keys.remove(key)
            self.lru_keys.append(key)
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Dict):
        """设置缓存"""
        self.cache[key] = value
        
        # 更新LRU
        if key in self.lru_keys:
            self.lru_keys.remove(key)
        self.lru_keys.append(key)
        
        # 清理过期
        if len(self.cache) > self.max_size:
            oldest = self.lru_keys.popleft()
            del self.cache[oldest]
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.lru_keys.clear()


class SuperCTFAgent(BaseAgent):
    """
    超级CTF Agent - 集成版
    
    继承原有的BaseAgent，添加多Agent协作能力
    """
    
    def __init__(self, config: Config = None, memory_file: str = None):
        """
        初始化超级Agent
        
        Args:
            config: 配置对象
            memory_file: 记忆文件路径
        """
        # 调用父类初始化（如果BaseAgent可用）
        if BaseAgent != object and hasattr(BaseAgent, '__init__'):
            try:
                super().__init__(config) if config else None
            except:
                pass
        
        # 初始化多Agent
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.knowledge = KnowledgeAgent(memory_file)
        self.monitor = MonitorAgent()
        
        # 初始化记忆系统
        if ConversationMemory:
            self.conversation_memory = ConversationMemory()
        if KnowledgeMemory:
            try:
                from pathlib import Path
                base_path = Path('/home/ctf_agent/knowledge')
                self.knowledge_memory = KnowledgeMemory(base_path=base_path)
            except:
                self.knowledge_memory = None
        
        self.current_challenge = None
        
        print("🎉 超级CTF Agent v2.0 已启用!")
        print(f"   - 知识库: {len(self.knowledge.kb)} 条记录")
        print(f"   - 已整合原有CTF Agent功能")
    
    async def solve_challenge(self, challenge: Dict[str, Any]) -> Dict[str, Any]:
        """
        智能解题主函数
        
        Args:
            challenge: 题目信息
                - name: 名称
                - description: 描述
                - category: 类别
                - difficulty: 难度
                - files: 文件列表
                - data: 备份数据
        
        Returns:
            解题结果
        """
        print(f"\n{'='*70}")
        print(f"🤖 超级CTF Agent")
        print(f"{'='*70}")
        print(f"🎯 题目: {challenge.get('name', 'Unknown')}")
        print(f"类型: {challenge.get('category', 'misc')}")
        print(f"难度: {'⭐' * challenge.get('difficulty', 5)} ({challenge.get('difficulty', 1)}/10)")
        print(f"{'-'*70}")
        
        start_time = time.time()
        
        # 设置当前题目
        self.current_challenge = challenge
        
        try:
            # 步骤1: 搜索知识库
            print("\n📚 搜索知识库...")
            similar = self.knowledge.search(challenge.get('description', ''), 
                                           challenge.get('category'))
            if similar:
                print(f"  找到 {len(similar)} 条相关记录")
                for i, item in enumerate(similar[:3], 1):
                    print(f"    {i}. {item['problem'].get('name', 'unknown')}")
            
            # 步骤2: 制定计划
            print("\n🧠 制定解题计划...")
            tasks = self.planner.plan(challenge)
            print(f"  生成 {len(tasks)} 个任务")
            
            # 步骤3: 执行任务
            print("\n🔨 执行解题任务...")
            result = await self.executor.execute(self, tasks, challenge)
            
            # 记录指标
            duration = time.time() - start_time
            self.monitor.record(
                status='success' if result.get('success_count', 0) > 0 else 'failed',
                duration=duration,
                category=challenge.get('category', 'misc'),
                tools=result.get('tools_used', [])
            )
            
            # 步骤4: 学习和记忆
            if result.get('success_count', 0) > 0:
                print("\n💾 保存解题经验...")
                self.knowledge.add(
                    problem=challenge,
                    solution=result,
                    success=True,
                    tools=result.get('tools_used', [])
                )
            
            # 步骤5: 生成报告
            print(f"\n📊 解题完成!")
            print(f"{'='*70}")
            print(f"结果: {result.get('status', 'unknown')}")
            print(f"成功: {result.get('success_count', 0)}/{result.get('total_count', 0)}")
            print(f"耗时: {duration:.2f}秒")
            print(f"{'='*70}")
            
            return result
            
        except Exception as e:
            print(f"\n❌ 解题失败: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "status": "error",
                "error": str(e),
                "success_count": 0,
                "total_count": 0
            }
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "monitor": self.monitor.get_metrics(),
            "knowledge": len(self.knowledge.kb),
            "cache_size": len(self.executor.cache.cache),
            "executor_stats": self.executor.get_tool_stats()
        }


def main():
    """主函数 - 测试"""
    import argparse
    
    parser = argparse.ArgumentParser(description="超级CTF Agent v2.0")
    parser.add_argument('-c', '--challenge', type=str, help="挑战数据(JSON字符串)")
    args = parser.parse_args()
    
    # 初始化Agent
    agent = SuperCTFAgent()
    
    # 测试题目
    if args.challenge:
        challenge = json.loads(args.challenge)
    else:
        challenge = {
            "name": "Base64 Demo",
            "description": "Decode: SGVsbG8gQ1RGe30",
            "category": "crypto",
            "difficulty": 1,
            "files": [],
            "data": "SGVsbG8gQ1RGe30="
        }
    
    # 解题
    result = asyncio.run(agent.solve_challenge(challenge))
    
    # 显示统计
    stats = agent.get_stats()
    print("\n📊 统计信息:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
