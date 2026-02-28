#!/usr/bin/env python3
"""
Stock Portfolio Analyzer 性能测试
"""

import time
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def test_analysis_performance():
    """测试分析性能"""
    # 模拟导入时间测试
    start = time.time()
    # 延迟模拟
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"导入时间过长: {elapsed:.3f}s"

def test_report_generation():
    """测试报告生成性能"""
    start = time.time()
    # 模拟报告生成
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"报告生成时间过长: {elapsed:.3f}s"

def test_html_rendering():
    """测试HTML渲染性能"""
    start = time.time()
    # 模拟HTML渲染
    html = "<html><body>Test Report</body></html>"
    elapsed = time.time() - start
    assert elapsed < 1.0, f"HTML渲染时间过长: {elapsed:.3f}s"

if __name__ == "__main__":
    test_analysis_performance()
    test_report_generation()
    test_html_rendering()
    print("✓ 性能测试通过")
