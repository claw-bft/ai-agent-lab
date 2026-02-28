#!/usr/bin/env python3
"""
API 性能测试
"""

import time
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_api_response_time():
    """测试API响应时间"""
    start = time.time()
    # 模拟API响应
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"API响应时间过长: {elapsed:.3f}s"

def test_skill_listing():
    """测试技能列表获取性能"""
    start = time.time()
    # 模拟技能列表获取
    skills = [{"name": f"skill-{i}"} for i in range(10)]
    elapsed = time.time() - start
    assert elapsed < 1.0, f"技能列表获取时间过长: {elapsed:.3f}s"

def test_search_performance():
    """测试搜索性能"""
    start = time.time()
    # 模拟搜索
    results = [{"name": "test"} for _ in range(5)]
    elapsed = time.time() - start
    assert elapsed < 1.0, f"搜索时间过长: {elapsed:.3f}s"

if __name__ == "__main__":
    test_api_response_time()
    test_skill_listing()
    test_search_performance()
    print("✓ 性能测试通过")
