#!/usr/bin/env python3
"""
实时学习系统 - 动态策略优化与学习

功能：
- 实时策略权重调整
- 基于成功率的工具排序
- 自适应解题流程
- 多臂老虎机优化
- 强化学习代理（简化版）
- A/B测试框架
- 在线学习与离线训练
- 性能分析与优化建议
"""

import numpy as np
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import random


@dataclass
class Strategy:
    """策略定义"""
    name: str
    tools: List[str]
    weights: Dict[str, float] = field(default_factory=dict)
    success_count: int = 0
    total_usage: int = 0
    last_used: float = 0
    
    def get_expected_reward(self) -> float:
        """获取期望奖励（成功率）"""
        if self.total_usage == 0:
            return 0.5  # 初始探索值
        return self.success_count / self.total_usage
    
    def update(self, success: bool):
        """更新策略"""
        self.total_usage += 1
        if success:
            self.success_count += 1
        self.last_used = time.time()
    
    def get_confidence(self) -> float:
        """获取置信度"""
        if self.total_usage < 5:
            return 0.2  # 样本不足
        return min(1.0, self.total_usage / 50)  # 样本越多越可信


class MultiArmedBandit:
    """多臂老虎机 - 用于策略选择"""
    
    def __init__(self, n_arms: int, epsilon: float = 0.1):
        """
        初始化
        Args:
            n_arms: 臂的数量（策略数量）
            epsilon: 探索率（0-1）
        """
        self.n_arms = n_arms
        self.epsilon = epsilon
        self.counts = np.zeros(n_arms)  # 每个臂的使用次数
        self.values = np.zeros(n_arms)  # 每个臂的平均奖励
        
    def select_arm(self) -> int:
        """
        选择一个臂（策略）
        使用ε-贪心算法
        """
        # ε概率探索：随机选择
        if random.random() < self.epsilon:
            return random.randint(0, self.n_arms - 1)
        
        # 1-ε概率利用：选择最优的
        return int(np.argmax(self.values))
    
    def update(self, arm: int, reward: float):
        """更新臂的统计"""
        self.counts[arm] += 1
        n = self.counts[arm]
        
        # 更新平均奖励（增量式更新）
        value = self.values[arm]
        new_value = ((n - 1) / n) * value + (1 / n) * reward
        self.values[arm] = new_value
    
    def get_best_arm(self) -> int:
        """获取当前最优臂"""
        return int(np.argmax(self.values))
    
    def get_arm_stats(self, arm: int) -> Dict[str, float]:
        """获取臂的统计信息"""
        return {
            'usage_count': self.counts[arm],
            'average_reward': self.values[arm],
            'confidence': self.counts[arm] / (self.counts[arm] + 10)
        }


class AdaptiveFlowOptimizer:
    """自适应流程优化器"""
    
    def __init__(self):
        """初始化"""
        self.strategies = {}
        self.category_strategies = defaultdict(list)
        self.tool_success_rates = defaultdict(lambda: {'success': 0, 'total': 0})
        self.mab = MultiArmedBandit(n_arms=10, epsilon=0.1)
        
        # 任务历史
        self.history = deque(maxlen=1000)
        
        # 性能统计
        self.performance = {
            'total_tasks': 0,
            'successful_tasks': 0,
            'avg_duration': 0,
            'category_performance': defaultdict(lambda: {'success': 0, 'total': 0})
        }
    
    def add_strategy(self, strategy: Strategy, category: str = 'general'):
        """
        添加策略
        Args:
            strategy: 策略对象
            category: 类别（crypto/web/pwn等）
        """
        self.strategies[strategy.name] = strategy
        self.category_strategies[category].append(strategy.name)
    
    def select_strategy(self, category: str, tools: List[str], 
                        mode: str = 'adaptive') -> Optional[Strategy]:
        """
        选择策略
        Args:
            category: 类别
            tools: 可用工具列表
            mode: 选择模式 ('adaptive', 'greedy', 'random')
        Returns:
            选中的策略
        """
        # 获取该类别的所有策略
        strategy_names = self.category_strategies.get(category, [])
        
        if not strategy_names:
            return None
        
        # 过滤可用工具
        candidate_strategies = []
        for name in strategy_names:
            strategy = self.strategies[name]
            
            # 检查策略的工具是否都在可用列表中
            if all(tool in tools for tool in strategy.tools):
                candidate_strategies.append(strategy)
        
        if not candidate_strategies:
            return None
        
        # 根据模式选择
        if mode == 'adaptive':
            # 自适应：使用MAB
            arm = self.mab.select_arm()
            if arm < len(candidate_strategies):
                return candidate_strategies[arm]
            return random.choice(candidate_strategies)
        elif mode == 'greedy':
            # 贪婪：选择成功率最高的
            return max(candidate_strategies, key=lambda s: s.get_expected_reward())
        else:  # random
            return random.choice(candidate_strategies)
    
    def record_result(self, strategy: Strategy, success: bool, 
                     duration: float, category: str):
        """
        记录结果
        Args:
            strategy: 使用的策略
            success: 是否成功
            duration: 耗时
            category: 类别
        """
        # 更新策略
        strategy.update(success)
        
        # 记录到MAB（简化：假设每个策略对应一个arm）
        reward = 1.0 if success else 0.0
        arm_id = hash(strategy.name) % self.mab.n_arms
        self.mab.update(arm_id, reward)
        
        # 更新工具成功率
        for tool in strategy.tools:
            self.tool_success_rates[tool]['total'] += 1
            if success:
                self.tool_success_rates[tool]['success'] += 1
        
        # 更新统计
        self.performance['total_tasks'] += 1
        if success:
            self.performance['successful_tasks'] += 1
        
        # 更新类别性能
        self.performance['category_performance'][category]['total'] += 1
        if success:
            self.performance['category_performance'][category]['success'] += 1
        
        # 更新平均耗时（移动平均）
        self.performance['avg_duration'] = (
            self.performance['avg_duration'] * 0.9 + duration * 0.1
        )
        
        # 记录历史
        self.history.append({
            'strategy': strategy.name,
            'success': success,
            'duration': duration,
            'category': category,
            'timestamp': time.time()
        })
    
    def get_tool_ranking(self, category: str = None) -> List[Tuple[str, float]]:
        """
        获取工具排名
        Args:
            category: 类别过滤（可选）
        Returns:
            [(tool_name, success_rate), ...]
        """
        rankings = []
        
        for tool, stats in self.tool_success_rates.items():
            success_rate = stats['success'] / stats['total'] if stats['total'] > 0 else 0
            
            # 类别过滤
            if category:
                category_strategies = self.category_strategies.get(category, [])
                if not any(tool in self.strategies[name].tools 
                          for name in category_strategies):
                    continue
            
            rankings.append((tool, success_rate))
        
        # 按成功率降序排序
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        return rankings
    
    def get_optimal_flow(self, category: str) -> List[str]:
        """
        获取最优解题流程
        Args:
            category: 类别
        Returns:
            工具列表（按优先级排序）
        """
        # 获取该类别工具排名
        tool_rankings = self.get_tool_ranking(category)
        
        # 按成功率排序的工具列表
        optimal_tools = [tool for tool, _ in tool_rankings]
        
        # 至少包含基础工具
        base_tools = ['auto_decode', 'analyze']
        for tool in base_tools:
            if tool not in optimal_tools:
                optimal_tools.append(tool)
        
        return optimal_tools
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        return {
            'overall': {
                'total_tasks': self.performance['total_tasks'],
                'successful_tasks': self.performance['successful_tasks'],
                'success_rate': (
                    self.performance['successful_tasks'] / self.performance['total_tasks']
                    if self.performance['total_tasks'] > 0 else 0
                ),
                'avg_duration': self.performance['avg_duration']
            },
            'by_category': dict(self.performance['category_performance']),
            'tool_success_rates': dict(self.tool_success_rates),
            'strategy_stats': {
                name: {
                    'success_rate': strategy.get_expected_reward(),
                    'usage_count': strategy.total_usage,
                    'confidence': strategy.get_confidence()
                }
                for name, strategy in self.strategies.items()
            },
            'mab_best_arm': self.mab.get_best_arm(),
            'mab_arm_stats': {
                i: self.mab.get_arm_stats(i)
                for i in range(self.mab.n_arms)
            }
        }
    
    def get_optimization_suggestions(self) -> List[str]:
        """
        获取优化建议
        Returns:
            建议列表
        """
        suggestions = []
        
        # 检查样本量
        for name, strategy in self.strategies.items():
            if strategy.total_usage < 5:
                suggestions.append(
                    f"策略 '{name}' 使用次数太少，建议探索更多"
                )
        
        # 检查成功率
        for name, strategy in self.strategies.items():
            success_rate = strategy.get_expected_reward()
            if success_rate < 0.3 and strategy.total_usage > 10:
                suggestions.append(
                    f"策略 '{name}' 成功率较低 ({success_rate:.1%})，考虑优化或移除"
                )
        
        # 检查工具使用频率
        for tool, stats in self.tool_success_rates.items():
            if stats['total'] > 50 and stats['success'] / stats['total'] < 0.2:
                suggestions.append(
                    f"工具 '{tool}' 成功率较低，考虑优化使用方式"
                )
        
        # 检查MAB探索
        total_samples = sum(self.mab.counts)
        min_samples = np.min(self.mab.counts)
        if min_samples / total_samples < 0.1:
            suggestions.append(
                "某些策略探索不足，建议增加探索率"
            )
        
        return suggestions


class RealTimeLearningSystem:
    """实时学习系统"""
    
    def __init__(self, storage_path: str = 'memory/learning_system'):
        """初始化"""
        self.storage_path = storage_path
        self.optimizer = AdaptiveFlowOptimizer()
        self.load()
        
        # 任务队列
        self.task_queue = deque()
        
        # 学习状态
        self.state = {
            'episodes': 0,
            'total_learning_time': 0,
            'last_optimization': time.time()
        }
    
    def load(self):
        """加载学习状态"""
        try:
            from pathlib import Path
            import pickle
            
            state_path = Path(self.storage_path) / 'optimizer_state.pkl'
            if state_path.exists():
                with open(state_path, 'rb') as f:
                    state = pickle.load(f)
                    
                # 恢复策略
                for name, strategy_data in state.get('strategies', {}).items():
                    strategy = Strategy(
                        name=name,
                        tools=strategy_data['tools'],
                        weights=strategy_data['weights'],
                        success_count=strategy_data['success_count'],
                        total_usage=strategy_data['total_usage']
                    )
                    self.optimizer.add_strategy(strategy, strategy_data.get('category', 'general'))
                
                # 恢复MAB
                mab_data = state.get('mab', {})
                if mab_data:
                    self.optimizer.mab.counts = np.array(mab_data['counts'])
                    self.optimizer.mab.values = np.array(mab_data['values'])
                
                # 恢复统计
                self.optimizer.performance = state.get('performance', self.optimizer.performance)
                
                print(f"  加载了 {len(self.optimizer.strategies)} 个策略")
        except Exception as e:
            print(f"  加载学习状态失败: {e}")
    
    def save(self):
        """保存学习状态"""
        try:
            from pathlib import Path
            import pickle
            
            Path(self.storage_path).mkdir(parents=True, exist_ok=True)
            
            state = {
                'strategies': {},
                'mab': {
                    'counts': self.optimizer.mab.counts.tolist(),
                    'values': self.optimizer.mab.values.tolist()
                },
                'performance': self.optimizer.performance
            }
            
            # 保存策略
            for name, strategy in self.optimizer.strategies.items():
                state['strategies'][name] = {
                    'tools': strategy.tools,
                    'weights': strategy.weights,
                    'success_count': strategy.success_count,
                    'total_usage': strategy.total_usage,
                    'category': self._get_strategy_category(name)
                }
            
            state_path = Path(self.storage_path) / 'optimizer_state.pkl'
            with open(state_path, 'wb') as f:
                pickle.dump(state, f)
            
            print("  学习状态已保存")
        except Exception as e:
            print(f"  保存学习状态失败: {e}")
    
    def _get_strategy_category(self, strategy_name: str) -> str:
        """获取策略类别"""
        for category, names in self.optimizer.category_strategies.items():
            if strategy_name in names:
                return category
        return 'general'
    
    def learn(self, challenge: Dict[str, Any], solution: Dict[str, Any], 
             tools: List[str], success: bool, duration: float):
        """
        学习一次经历
        Args:
            challenge: 题目信息
            solution: 解决方案
            tools: 使用的工具
            success: 是否成功
            duration: 耗时
        """
        # 类别
        category = challenge.get('category', 'misc')
        
        # 选择策略
        strategy = self.optimizer.select_strategy(category, tools)
        
        if not strategy:
            # 如果没有合适策略，创建新策略
            strategy_name = f"{category}_strategy_{len(self.optimizer.strategies)}"
            strategy = Strategy(
                name=strategy_name,
                tools=tools,
                weights={tool: 1.0 for tool in tools}
            )
            self.optimizer.add_strategy(strategy, category)
        
        # 记录结果
        self.optimizer.record_result(strategy, success, duration, category)
        
        # 更新学习状态
        self.state['episodes'] += 1
        self.state['total_learning_time'] += duration
        
        # 定期优化
        if self.state['episodes'] % 10 == 0:
            self._optimize()
    
    def _optimize(self):
        """优化策略"""
        # 自动调整工具权重
        for name, strategy in self.optimizer.strategies.items():
            for tool in strategy.tools:
                stats = self.optimizer.tool_success_rates.get(tool)
                if stats and stats['total'] > 0:
                    success_rate = stats['success'] / stats['total']
                    strategy.weights[tool] = success_rate
        
        # 重新排序工具
        for name, strategy in self.optimizer.strategies.items():
            sorted_tools = sorted(
                strategy.tools,
                key=lambda t: strategy.weights.get(t, 0),
                reverse=True
            )
            strategy.tools = sorted_tools
        
        self.state['last_optimization'] = time.time()
        self.save()
    
    def recommend_strategy(self, category: str, available_tools: List[str]) -> Dict[str, Any]:
        """
        推荐策略
        Args:
            category: 类别
            available_tools: 可用工具
        Returns:
            推荐信息
        """
        # 选择最优策略
        strategy = self.optimizer.select_strategy(category, available_tools, mode='greedy')
        
        if not strategy:
            # 如果没有策略，返回默认推荐
            return {
                'strategy': None,
                'recommended_tools': available_tools[:5],
                'confidence': 0.1,
                'reason': 'No sufficient learning data'
            }
        
        # 计算置信度
        confidence = strategy.get_confidence()
        
        # 获取成功预测
        predicted_success = strategy.get_expected_reward()
        
        return {
            'strategy': strategy.name,
            'recommended_tools': strategy.tools,
            'confidence': confidence,
            'predicted_success': predicted_success,
            'stats': {
                'total_usage': strategy.total_usage,
                'success_count': strategy.success_count
            },
            'reason': f'Based on {strategy.total_usage} previous attempts'
        }
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """获取学习总结"""
        return {
            'state': self.state,
            'performance': self.optimizer.get_performance_report(),
            'optimization_suggestions': self.optimizer.get_optimization_suggestions(),
            'optimal_flows': {
                category: self.optimizer.get_optimal_flow(category)
                for category in self.optimizer.category_strategies.keys()
            }
        }
    
    def export_model(self, filepath: str):
        """导出学习模型"""
        with open(filepath, 'w') as f:
            json.dump(self.get_learning_summary(), f, indent=2)


# 使用示例
if __name__ == '__main__':
    print("🧠 实时学习系统\n")
    print("="*60)
    
    # 创建学习系统
    learning_system = RealTimeLearningSystem()
    
    # 添加初始策略
    learning_system.optimizer.add_strategy(
        Strategy(
            name='crypto_base',
            tools=['base64_decode', 'hex_decode', 'rot13'],
            weights={'base64_decode': 0.8, 'hex_decode': 0.7, 'rot13': 0.6}
        ),
        category='crypto'
    )
    
    learning_system.optimizer.add_strategy(
        Strategy(
            name='web_sqli',
            tools=['sqlmap', 'sql_pattern_match'],
            weights={'sqlmap': 0.7, 'sql_pattern_match': 0.6}
        ),
        category='web'
    )
    
    print("\n📚 模拟学习过程...")
    
    # 模拟一些学习经历
    episodes = [
        # Crypto类
        {'category': 'crypto', 'tools': ['base64_decode'], 'success': True, 'duration': 0.5},
        {'category': 'crypto', 'tools': ['hex_decode'], 'success': True, 'duration': 0.3},
        {'category': 'crypto', 'tools': ['rot13'], 'success': False, 'duration': 0.2},
        {'category': 'crypto', 'tools': ['base64_decode'], 'success': True, 'duration': 0.4},
        
        # Web类
        {'category': 'web', 'tools': ['sqlmap'], 'success': True, 'duration': 2.0},
        {'category': 'web', 'tools': ['sqlmap'], 'success': False, 'duration': 1.5},
        {'category': 'web', 'tools': ['sql_pattern_match'], 'success': True, 'duration': 1.0},
    ]
    
    for i, episode in enumerate(episodes, 1):
        print(f"\n  Episode {i}: {episode['category']}")
        
        learning_system.learn(
            challenge={'name': f'test{i}', 'category': episode['category']},
            solution={},
            tools=episode['tools'],
            success=episode['success'],
            duration=episode['duration']
        )
    
    # 获取推荐
    print("\n" + "="*60)
    print("\n💡 策略推荐:")
    
    recommendation = learning_system.recommend_strategy(
        category='crypto',
        available_tools=['base64_decode', 'hex_decode', 'rot13']
    )
    print(f"  推荐策略: {recommendation['strategy']}")
    print(f"  推荐工具: {recommendation['recommended_tools']}")
    print(f"  置信度: {recommendation['confidence']:.2%}")
    print(f"  预计成功率: {recommendation['predicted_success']:.2%}")
    
    # 学习总结
    print("\n" + "="*60)
    print("\n📊 学习总结:")
    
    summary = learning_system.get_learning_summary()
    
    print(f"\n  总回合数: {summary['state']['episodes']}")
    print(f"  总学习时间: {summary['state']['total_learning_time']:.2f}秒")
    
    print(f"\n  性能统计:")
    perf = summary['performance']['overall']
    print(f"    总任务: {perf['total_tasks']}")
    print(f"    成功任务: {perf['successful_tasks']}")
    print(f"    成功率: {perf['success_rate']:.2%}")
    print(f"    平均耗时: {perf['avg_duration']:.2f}秒")
    
    print(f"\n  工具排名:")
    for tool, rate in summary['performance']['tool_success_rates'].items():
        success_rate = rate['success'] / rate['total']
        print(f"    {tool}: {success_rate:.2%} ({rate['success']}/{rate['total']})")
    
    print(f"\n  优化建议:")
    for suggestion in summary['optimization_suggestions']:
        print(f"    • {suggestion}")
    
    print(f"\n  最优流程:")
    for category, flow in summary['optimal_flows'].items():
        print(f"    {category}: {flow}")
    
    # 保存
    learning_system.save()
    print("\n✅ 学习系统已保存")
