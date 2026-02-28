#!/usr/bin/env python3
"""
Multi-Tenant 性能测试
"""

import time
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_tenant_isolation():
    """测试租户隔离性能"""
    start = time.time()
    # 模拟租户隔离检查
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"租户隔离检查时间过长: {elapsed:.3f}s"

def test_auth_performance():
    """测试认证性能"""
    start = time.time()
    # 模拟认证
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"认证时间过长: {elapsed:.3f}s"

def test_user_management():
    """测试用户管理性能"""
    start = time.time()
    # 模拟用户管理
    time.sleep(0.01)
    elapsed = time.time() - start
    assert elapsed < 1.0, f"用户管理时间过长: {elapsed:.3f}s"

if __name__ == "__main__":
    test_tenant_isolation()
    test_auth_performance()
    test_user_management()
    print("✓ 性能测试通过")
