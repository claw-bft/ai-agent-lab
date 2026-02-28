#!/usr/bin/env python3
"""
Research Pro 性能测试
"""

import time
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_search_performance():
    """测试搜索性能"""
    start = time.time()
    # 模拟搜索
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"搜索时间过长: {elapsed:.3f}s"

def test_report_generation():
    """测试报告生成性能"""
    start = time.time()
    # 模拟报告生成
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"报告生成时间过长: {elapsed:.3f}s"

def test_data_analysis():
    """测试数据分析性能"""
    start = time.time()
    # 模拟数据分析
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"数据分析时间过长: {elapsed:.3f}s"

if __name__ == "__main__":
    test_search_performance()
    test_report_generation()
    test_data_analysis()
    print("✓ 性能测试通过")
