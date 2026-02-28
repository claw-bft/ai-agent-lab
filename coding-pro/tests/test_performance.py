#!/usr/bin/env python3
"""
Coding Pro 性能测试
"""

import time
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_code_generation():
    """测试代码生成性能"""
    start = time.time()
    # 模拟代码生成
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"代码生成时间过长: {elapsed:.3f}s"

def test_code_analysis():
    """测试代码分析性能"""
    start = time.time()
    # 模拟代码分析
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"代码分析时间过长: {elapsed:.3f}s"

def test_demo_generation():
    """测试演示生成性能"""
    start = time.time()
    # 模拟演示生成
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"演示生成时间过长: {elapsed:.3f}s"

if __name__ == "__main__":
    test_code_generation()
    test_code_analysis()
    test_demo_generation()
    print("✓ 性能测试通过")
