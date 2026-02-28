"""
租户管理器测试
"""

import unittest
from datetime import datetime

import sys
sys.path.insert(0, '/root/.openclaw/workspace/ai-agent-lab/multi-tenant')

from core.tenant_manager import TenantManager, TenantStatus, TenantTier


class TestTenantManager(unittest.TestCase):
    """测试租户管理器"""

    def setUp(self):
        """测试前准备"""
        self.manager = TenantManager()

    def test_create_tenant(self):
        """测试创建租户"""
        tenant = self.manager.create_tenant(
            name="Test Company",
            owner_id="user_123",
            tier=TenantTier.STARTER,
        )

        self.assertIsNotNone(tenant.id)
        self.assertEqual(tenant.name, "Test Company")
        self.assertEqual(tenant.slug, "test-company")
        self.assertEqual(tenant.owner_id, "user_123")
        self.assertEqual(tenant.tier, TenantTier.STARTER)
        self.assertEqual(tenant.status, TenantStatus.ACTIVE)

    def test_create_tenant_invalid_name(self):
        """测试创建租户时名称无效"""
        with self.assertRaises(ValueError):
            self.manager.create_tenant(name="", owner_id="user_123")

        with self.assertRaises(ValueError):
            self.manager.create_tenant(name="a", owner_id="user_123")

    def test_create_tenant_duplicate_slug(self):
        """测试创建租户时slug自动去重"""
        tenant1 = self.manager.create_tenant(
            name="Test Company",
            owner_id="user_1",
        )
        tenant2 = self.manager.create_tenant(
            name="Test Company",
            owner_id="user_2",
        )

        self.assertEqual(tenant1.slug, "test-company")
        self.assertEqual(tenant2.slug, "test-company-1")

    def test_get_tenant(self):
        """测试获取租户"""
        tenant = self.manager.create_tenant(
            name="Test Company",
            owner_id="user_123",
        )

        # 通过ID获取
        found = self.manager.get_tenant(tenant.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, tenant.id)

        # 通过slug获取
        found_by_slug = self.manager.get_tenant_by_slug(tenant.slug)
        self.assertIsNotNone(found_by_slug)
        self.assertEqual(found_by_slug.id, tenant.id)

        # 获取不存在的租户
        not_found = self.manager.get_tenant("non_existent")
        self.assertIsNone(not_found)

    def test_list_tenants(self):
        """测试列出租户"""
        # 创建多个租户
        self.manager.create_tenant(name="Company A", owner_id="user_1", tier=TenantTier.FREE)
        self.manager.create_tenant(name="Company B", owner_id="user_2", tier=TenantTier.PROFESSIONAL)
        self.manager.create_tenant(name="Company C", owner_id="user_3", tier=TenantTier.FREE)

        # 列出所有
        all_tenants = self.manager.list_tenants()
        self.assertEqual(len(all_tenants), 3)

        # 按等级筛选
        free_tenants = self.manager.list_tenants(tier=TenantTier.FREE)
        self.assertEqual(len(free_tenants), 2)

        # 按状态筛选
        active_tenants = self.manager.list_tenants(status=TenantStatus.ACTIVE)
        self.assertEqual(len(active_tenants), 3)

    def test_update_tenant(self):
        """测试更新租户"""
        tenant = self.manager.create_tenant(
            name="Test Company",
            owner_id="user_123",
        )

        # 更新名称
        updated = self.manager.update_tenant(
            tenant.id,
            name="Updated Company",
            tier=TenantTier.ENTERPRISE,
        )

        self.assertIsNotNone(updated)
        self.assertEqual(updated.name, "Updated Company")
        self.assertEqual(updated.tier, TenantTier.ENTERPRISE)

        # 更新不存在的租户
        not_found = self.manager.update_tenant("non_existent", name="Test")
        self.assertIsNone(not_found)

    def test_delete_tenant(self):
        """测试删除租户"""
        tenant = self.manager.create_tenant(
            name="Test Company",
            owner_id="user_123",
        )

        # 软删除
        result = self.manager.delete_tenant(tenant.id, soft_delete=True)
        self.assertTrue(result)

        deleted = self.manager.get_tenant(tenant.id)
        self.assertEqual(deleted.status, TenantStatus.DELETED)

        # 硬删除
        tenant2 = self.manager.create_tenant(
            name="Test Company 2",
            owner_id="user_123",
        )
        result = self.manager.delete_tenant(tenant2.id, soft_delete=False)
        self.assertTrue(result)

        not_found = self.manager.get_tenant(tenant2.id)
        self.assertIsNone(not_found)

    def test_get_quota_limits(self):
        """测试获取配额限制"""
        tenant = self.manager.create_tenant(
            name="Test Company",
            owner_id="user_123",
            tier=TenantTier.FREE,
        )

        quotas = self.manager.get_quota_limits(tenant.id)

        self.assertIn("max_users", quotas)
        self.assertIn("max_skills", quotas)
        self.assertIn("api_calls_per_day", quotas)

        # FREE等级限制
        self.assertEqual(quotas["max_users"], 3)

        # ENTERPRISE等级无限制
        enterprise_tenant = self.manager.create_tenant(
            name="Enterprise",
            owner_id="user_2",
            tier=TenantTier.ENTERPRISE,
        )
        enterprise_quotas = self.manager.get_quota_limits(enterprise_tenant.id)
        self.assertEqual(enterprise_quotas["max_users"], -1)


if __name__ == "__main__":
    unittest.main()
