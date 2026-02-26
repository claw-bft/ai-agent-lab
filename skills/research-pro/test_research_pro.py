#!/usr/bin/env python3
"""
Research Pro 测试套件
验证搜索适配器和研究功能
"""

import sys
import json
from pathlib import Path

# 添加技能包路径
sys.path.insert(0, str(Path(__file__).parent))

from search_adapter import SearchAdapter, search, batch_search


def test_search_adapter():
    """测试搜索适配器"""
    print("=" * 50)
    print("测试搜索适配器")
    print("=" * 50)
    
    adapter = SearchAdapter()
    status = adapter.get_status()
    
    print(f"\n[状态检测]")
    print(f"  可用后端: {status['backends']}")
    print(f"  首选后端: {status['preferred']}")
    print(f"  搜索可用: {status['available']}")
    
    return status['available']


def test_single_search():
    """测试单次搜索"""
    print("\n" + "=" * 50)
    print("测试单次搜索")
    print("=" * 50)
    
    query = "人工智能最新发展趋势"
    print(f"\n[搜索查询] {query}")
    
    results = search(query, limit=3)
    
    print(f"[结果数量] {len(results)}")
    
    if results and not results[0].get("error"):
        print("\n[搜索结果]")
        for i, r in enumerate(results[:3], 1):
            print(f"  {i}. {r.get('title', '无标题')}")
            print(f"     {r.get('snippet', '无摘要')[:80]}...")
        return True
    else:
        print(f"  警告: {results[0].get('error', '无结果')}")
        return False


def test_batch_search():
    """测试批量搜索"""
    print("\n" + "=" * 50)
    print("测试批量搜索")
    print("=" * 50)
    
    queries = [
        "Python编程技巧",
        "机器学习入门",
        "数据可视化工具"
    ]
    
    print(f"\n[批量查询] {len(queries)} 个")
    
    results = batch_search(queries, limit=2)
    
    for query, items in results.items():
        print(f"  - {query}: {len(items)} 条结果")
    
    return True


def test_deduplication():
    """测试去重功能"""
    print("\n" + "=" * 50)
    print("测试去重功能")
    print("=" * 50)
    
    adapter = SearchAdapter()
    
    # 模拟有重复的结果
    test_results = [
        {"title": "结果1", "url": "http://example.com/1"},
        {"title": "结果2", "url": "http://example.com/2"},
        {"title": "结果1重复", "url": "http://example.com/1"},  # 重复URL
        {"title": "结果3", "url": "http://example.com/3"},
    ]
    
    print(f"\n[原始结果] {len(test_results)} 条")
    
    deduped = adapter.deduplicate_results(test_results)
    
    print(f"[去重后] {len(deduped)} 条")
    
    return len(deduped) == 3  # 应该剩下3条


def test_research_pro():
    """测试 Research Pro 主模块"""
    print("\n" + "=" * 50)
    print("测试 Research Pro 主模块")
    print("=" * 50)
    
    try:
        from research_pro import deep_research, realtime_search
        
        # 测试实时搜索
        print("\n[测试实时搜索]")
        result = realtime_search("OpenAI GPT-5", sources=["news"])
        
        if result.get("success"):
            print(f"  ✓ 搜索成功")
            print(f"  后端: {result.get('backend', 'unknown')}")
            print(f"  结果: {result.get('count', 0)} 条")
        else:
            print(f"  ✗ 搜索失败: {result.get('error')}")
        
        return result.get("success", False)
        
    except Exception as e:
        print(f"  ✗ 测试异常: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Research Pro 测试套件")
    print("=" * 60)
    
    tests = [
        ("搜索适配器", test_search_adapter),
        ("单次搜索", test_single_search),
        ("批量搜索", test_batch_search),
        ("去重功能", test_deduplication),
        ("Research Pro", test_research_pro),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n✗ {name} 测试异常: {e}")
            results.append((name, False))
    
    # 测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for name, p in results:
        status = "✓ 通过" if p else "✗ 失败"
        print(f"  {status}: {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
