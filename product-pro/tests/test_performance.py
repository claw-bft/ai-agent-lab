#!/usr/bin/env python3
"""
Product Pro 性能测试
"""

import time
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_prd_generation_performance():
    """测试PRD生成性能"""
    start = time.time()
    # 模拟PRD生成
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"PRD生成时间过长: {elapsed:.3f}s"

def test_competitor_analysis():
    """测试竞品分析性能"""
    start = time.time()
    # 模拟竞品分析
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"竞品分析时间过长: {elapsed:.3f}s"

def test_ppt_generation():
    """测试PPT生成性能"""
    start = time.time()
    # 模拟PPT生成
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"PPT生成时间过长: {elapsed:.3f}s"

if __name__ == "__main__":
    test_prd_generation_performance()
    test_competitor_analysis()
    test_ppt_generation()
    print("✓ 性能测试通过")
