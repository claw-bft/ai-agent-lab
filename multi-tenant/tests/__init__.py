"""
多租户系统测试套件
"""

import unittest
from datetime import datetime

# 导入测试模块
from .test_tenant_manager import TestTenantManager
from .test_tenant_context import TestTenantContext
from .test_isolation import TestResourceIsolator
from .test_auth import TestAuthManager


def create_test_suite():
    """创建测试套件"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestTenantManager))
    suite.addTests(loader.loadTestsFromTestCase(TestTenantContext))
    suite.addTests(loader.loadTestsFromTestCase(TestResourceIsolator))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthManager))
    
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(create_test_suite())
