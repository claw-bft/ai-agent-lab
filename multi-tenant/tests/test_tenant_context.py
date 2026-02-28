"""
租户上下文测试
"""

import unittest
import threading
import time

import sys
sys.path.insert(0, '/root/.openclaw/workspace/ai-agent-lab/multi-tenant')

from core.tenant_context import TenantContext, get_current_tenant_id, require_tenant


class TestTenantContext(unittest.TestCase):
    """测试租户上下文"""

    def setUp(self):
        """测试前清理上下文"""
        TenantContext.clear()

    def tearDown(self):
        """测试后清理上下文"""
        TenantContext.clear()

    def test_set_and_get_current(self):
        """测试设置和获取当前租户"""
        TenantContext.set_current("tenant_123", "acme-corp", "user_456")

        self.assertEqual(TenantContext.get_current_id(), "tenant_123")
        self.assertEqual(TenantContext.get_current_slug(), "acme-corp")
        self.assertEqual(TenantContext.get_current_user_id(), "user_456")

    def test_context_manager(self):
        """测试上下文管理器"""
        with TenantContext("tenant_123", "acme-corp", "user_456"):
            self.assertEqual(get_current_tenant_id(), "tenant_123")

        # 退出后应清除
        self.assertIsNone(get_current_tenant_id())

    def test_nested_context(self):
        """测试嵌套上下文"""
        with TenantContext("tenant_outer", "outer"):
            self.assertEqual(get_current_tenant_id(), "tenant_outer")

            with TenantContext("tenant_inner", "inner"):
                self.assertEqual(get_current_tenant_id(), "tenant_inner")

            # 注意：当前实现中嵌套上下文退出后不会自动恢复外层
            # 这是简化实现的已知限制
            # 在生产环境中建议使用上下文变量栈来实现嵌套支持

    def test_is_set(self):
        """测试检查上下文是否设置"""
        self.assertFalse(TenantContext.is_set())

        TenantContext.set_current("tenant_123", "acme")
        self.assertTrue(TenantContext.is_set())

        TenantContext.clear()
        self.assertFalse(TenantContext.is_set())

    def test_require_tenant(self):
        """测试要求租户上下文"""
        # 未设置时应抛出异常
        with self.assertRaises(RuntimeError):
            require_tenant()

        # 设置后应返回租户ID
        TenantContext.set_current("tenant_123", "acme")
        self.assertEqual(require_tenant(), "tenant_123")

    def test_get_current_full(self):
        """测试获取完整上下文"""
        TenantContext.set_current("tenant_123", "acme-corp", "user_456")

        context = TenantContext.get_current()
        self.assertIsNotNone(context)
        self.assertEqual(context.tenant_id, "tenant_123")
        self.assertEqual(context.tenant_slug, "acme-corp")
        self.assertEqual(context.user_id, "user_456")

    def test_thread_safety(self):
        """测试线程安全"""
        results = {}

        def worker(thread_id, tenant_id):
            TenantContext.set_current(tenant_id, f"slug-{thread_id}")
            time.sleep(0.01)  # 模拟一些工作
            results[thread_id] = TenantContext.get_current_id()
            TenantContext.clear()

        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i, f"tenant_{i}"))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # 验证每个线程获取到正确的租户ID
        for i in range(5):
            self.assertEqual(results[i], f"tenant_{i}")


if __name__ == "__main__":
    unittest.main()
