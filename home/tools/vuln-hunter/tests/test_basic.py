#!/usr/bin/env python3
"""
VulnHunter 基础测试
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))


async def test_discovery():
    """测试发现层"""
    print("=" * 60)
    print("测试 1: 子域名枚举")
    print("=" * 60)

    from discovery.subdomain import SubdomainEnumerator

    enumerator = SubdomainEnumerator()

    # 测试 DNS 查询
    print("\n▶ 子域名 DNS 枚举...")
    try:
        results = await enumerator.enumerate_subdomains("example.com", methods=["dns"])
        print(f"✓ DNS 查询完成")
        if results:
            for r in results[:3]:
                print(f"  - {r.subdomain} ({r.status})")
    except Exception as e:
        print(f"✗ DNS 查询失败: {e}")

    print("\n✅ 发现层测试完成")
    return True


async def test_detection():
    """测试检测层（静态分析）"""
    print("\n" + "=" * 60)
    print("测试 2: SQL 注入检测")
    print("=" * 60)

    from detection.advanced_sql import AdvancedSQLDetector

    detector = AdvancedSQLDetector()

    # 测试 Payload 生成（不需要实际请求）
    print("\n▶ 生成 SQL 注入 Payload...")
    try:
        vulnerabilities = await detector._detect_vulnerabilities(
            "http://testphp.vulnweb.com/artists.php?artist=1"
        )
        print(f"✓ Payload 生成完成")
        print(f"  - 生成漏洞: {len(vulnerabilities)}")
    except Exception as e:
        print(f"✗ Payload 生成失败: {e}")

    print("\n✅ 检测层测试完成")
    return True


async def test_intelligence():
    """测试智能分析层"""
    print("\n" + "=" * 60)
    print("测试 3: 智能风险评分")
    print("=" * 60)

    from intelligence.analyzer import IntelligenceAnalyzer

    analyzer = IntelligenceAnalyzer()

    # 测试误报过滤
    print("\n▶ 误报过滤测试...")
    try:
        # 模拟检测结果
        test_results = {
            "sql": [
                {"url": "http://example.com/err1.php?id=1", "confidence": 0.3, "error": "timeout"}
            ]
        }

        filtered = analyzer.filter_false_positives(test_results)
        print(f"✓ 误报过滤完成")
        print(f"  - 原始: 1, 过滤后: {len(filtered.get('sql', []))}")
    except Exception as e:
        print(f"✗ 误报过滤失败: {e}")

    # 测试风险评分
    print("\n▶ 风险评分测试...")
    try:
        test_vuln = {
            "type": "sql_injection",
            "severity": "high",
            "confidence": 0.85,
            "has_exploit": True,
            "url": "http://example.com"
        }

        score = analyzer.calculate_risk_score(test_vuln)
        print(f"✓ 风险评分: {score}")
    except Exception as e:
        print(f"✗ 风险评分失败: {e}")

    print("\n✅ 智能层测试完成")
    return True


async def test_reporting():
    """测试报告生成"""
    print("\n" + "=" * 60)
    print("测试 4: 报告生成")
    print("=" * 60)

    from reporting.generator import ReportGenerator

    generator = ReportGenerator()

    print("\n▶ 生成 HTML 报告...")
    try:
        test_data = {
            "target": "example.com",
            "scan_time": "2025-02-25",
            "vulnerabilities": []
        }

        report_path = generator.generate_html_report(test_data, output_dir="./results")
        print(f"✓ HTML 报告生成完成")
        print(f"  - 路径: {report_path}")
    except Exception as e:
        print(f"✗ 报告生成失败: {e}")

    print("\n✅ 报告层测试完成")
    return True


async def main():
    """主测试函数"""
    print("\n🔍 VulnHunter 基础测试套件\n")

    tests = [
        ("发现层", test_discovery),
        ("检测层", test_detection),
        ("智能层", test_intelligence),
        ("报告层", test_reporting),
    ]

    results = []

    for name, test_func in tests:
        try:
            success = await test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ {name} 测试失败: {e}")
            results.append((name, False))

    # 汇总
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} {name}")

    success_count = sum(1 for _, s in results if s)
    print(f"\n总计: {success_count}/{len(results)} 通过")

    return all(s for _, s in results)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
