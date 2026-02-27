#!/usr/bin/env python3
"""
自然语言执行层测试
"""

import sys
from pathlib import Path

# 添加被测代码路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from intent_parser import IntentParser, IntentType
from skill_router import SkillRouter
from executor import SkillExecutor, ExecutionStatus
from context_manager import ContextManager

def test_intent_parser():
    """测试意图解析器"""
    print("\n" + "=" * 60)
    print("测试: 意图解析器 (IntentParser)")
    print("=" * 60)
    
    parser = IntentParser()
    
    test_cases = [
        ("查询一下茅台股票", IntentType.GET_QUOTE),
        ("分析一下600519的走势", IntentType.ANALYZE_STOCK),
        ("帮我写一个Python爬虫", IntentType.GENERATE_CODE),
        ("研究一下AI发展趋势", IntentType.RESEARCH),
        ("分析竞品情况", IntentType.COMPETITOR_ANALYSIS),
        ("设置茅台股价超过1800的预警", IntentType.SET_ALERT),
        ("审查一下这个代码文件", IntentType.REVIEW_CODE),
        ("分析data.csv中的数据", IntentType.ANALYZE_DATA),
    ]
    
    passed = 0
    for text, expected_intent in test_cases:
        intent = parser.parse(text)
        status = "✓" if intent.type == expected_intent else "✗"
        if intent.type == expected_intent:
            passed += 1
        print(f"{status} '{text}'")
        print(f"   预期: {expected_intent.value}, 实际: {intent.type.value} (置信度: {intent.confidence:.2f})")
        if intent.entities:
            print(f"   实体: {intent.entities}")
    
    print(f"\n通过率: {passed}/{len(test_cases)}")
    return passed == len(test_cases)

def test_skill_router():
    """测试技能路由器"""
    print("\n" + "=" * 60)
    print("测试: 技能路由器 (SkillRouter)")
    print("=" * 60)
    
    parser = IntentParser()
    router = SkillRouter()
    
    test_cases = [
        ("查询茅台股票", "finance-pro", "quote"),
        ("分析600519", "finance-pro", "analyze"),
        ("写个Python函数", "coding-pro", "generate"),
        ("研究AI趋势", "research-pro", "deep"),
    ]
    
    passed = 0
    for text, expected_skill, expected_cmd in test_cases:
        intent = parser.parse(text)
        route = router.route(intent)
        
        skill_match = route.skill_name == expected_skill
        cmd_match = route.command == expected_cmd
        
        status = "✓" if skill_match and cmd_match else "✗"
        if skill_match and cmd_match:
            passed += 1
        
        print(f"{status} '{text}'")
        print(f"   路由: {route.skill_name}/{route.command}")
        print(f"   预期: {expected_skill}/{expected_cmd}")
        print(f"   置信度: {route.confidence:.2f}")
        print(f"   原因: {route.reason}")
    
    print(f"\n通过率: {passed}/{len(test_cases)}")
    return passed == len(test_cases)

def test_executor():
    """测试执行引擎"""
    print("\n" + "=" * 60)
    print("测试: 执行引擎 (SkillExecutor)")
    print("=" * 60)
    
    executor = SkillExecutor()
    
    # 测试自然语言执行
    test_cases = [
        "查询茅台股票",
        "研究AI发展趋势",
    ]
    
    for text in test_cases:
        print(f"\n📝 输入: {text}")
        result = executor.execute_natural_language(text)
        print(f"   技能: {result.skill_name}")
        print(f"   命令: {result.command}")
        print(f"   状态: {result.status.value}")
        print(f"   耗时: {result.duration_ms:.1f}ms")
        if result.output:
            output_str = str(result.output)
            print(f"   输出预览: {output_str[:150]}...")
    
    return True

def test_context_manager():
    """测试上下文管理器"""
    print("\n" + "=" * 60)
    print("测试: 上下文管理器 (ContextManager)")
    print("=" * 60)
    
    manager = ContextManager()
    session_id = "test_session_001"
    
    # 添加条目
    manager.add_entry(session_id, "user", "查询茅台股票", 
                     intent="get_quote", skill_used="finance-pro")
    manager.add_entry(session_id, "assistant", "茅台当前股价是1800元", 
                     skill_used="finance-pro")
    manager.add_entry(session_id, "user", "再查一下五粮液")
    
    # 获取上下文
    context = manager.get_context(session_id)
    print(f"✓ 上下文条目数: {len(context)}")
    
    # 检测跟进问题
    follow_up = manager.detect_follow_up(session_id, "还有呢")
    print(f"✓ 跟进检测: {'是' if follow_up and follow_up['is_follow_up'] else '否'}")
    if follow_up:
        print(f"   参考: {follow_up.get('reference', 'N/A')}")
    
    # 保存和加载
    saved = manager.save_session(session_id)
    print(f"✓ 会话保存: {'成功' if saved else '失败'}")
    
    # 统计
    stats = manager.get_session_stats(session_id)
    print(f"✓ 会话统计: {stats.get('total_entries')} 条记录")
    
    return True

def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("自然语言执行层 - 完整测试套件")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("IntentParser", test_intent_parser()))
    except Exception as e:
        print(f"✗ IntentParser 测试失败: {e}")
        results.append(("IntentParser", False))
    
    try:
        results.append(("SkillRouter", test_skill_router()))
    except Exception as e:
        print(f"✗ SkillRouter 测试失败: {e}")
        results.append(("SkillRouter", False))
    
    try:
        results.append(("SkillExecutor", test_executor()))
    except Exception as e:
        print(f"✗ SkillExecutor 测试失败: {e}")
        results.append(("SkillExecutor", False))
    
    try:
        results.append(("ContextManager", test_context_manager()))
    except Exception as e:
        print(f"✗ ContextManager 测试失败: {e}")
        results.append(("ContextManager", False))
    
    # 汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{status}: {name}")
    
    total = len(results)
    passed_count = sum(1 for _, p in results if p)
    
    print(f"\n总计: {passed_count}/{total} 通过")
    
    return passed_count == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
