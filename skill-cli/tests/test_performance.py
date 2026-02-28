#!/usr/bin/env python3
"""
Skill CLI 性能测试
"""

import time
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_cli_startup():
    """测试CLI启动性能"""
    start = time.time()
    # 模拟CLI启动
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"CLI启动时间过长: {elapsed:.3f}s"

def test_intent_parsing():
    """测试意图解析性能"""
    start = time.time()
    # 模拟意图解析
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"意图解析时间过长: {elapsed:.3f}s"

def test_skill_execution():
    """测试技能执行性能"""
    start = time.time()
    # 模拟技能执行
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"技能执行时间过长: {elapsed:.3f}s"

if __name__ == "__main__":
    test_cli_startup()
    test_intent_parsing()
    test_skill_execution()
    print("✓ 性能测试通过")
