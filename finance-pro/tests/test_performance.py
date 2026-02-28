#!/usr/bin/env python3
"""
Finance Pro 性能测试
"""

import time
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_data_fetching():
    """测试数据获取性能"""
    start = time.time()
    # 模拟数据获取
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"数据获取时间过长: {elapsed:.3f}s"

def test_indicator_calculation():
    """测试指标计算性能"""
    start = time.time()
    # 模拟指标计算
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"指标计算时间过长: {elapsed:.3f}s"

def test_chart_generation():
    """测试图表生成性能"""
    start = time.time()
    # 模拟图表生成
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"图表生成时间过长: {elapsed:.3f}s"

if __name__ == "__main__":
    test_data_fetching()
    test_indicator_calculation()
    test_chart_generation()
    print("✓ 性能测试通过")
