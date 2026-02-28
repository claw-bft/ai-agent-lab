"""
资源隔离器测试
"""

import unittest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, '/root/.openclaw/workspace/ai-agent-lab/multi-tenant')

from core.isolation import ResourceIsolator, DatabaseRouter


class TestResourceIsolator(unittest.TestCase):
    """测试资源隔离器"""
    
    def setUp(self):
        """测试前准备临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.isolator = ResourceIsolator(base_path=self.temp_dir)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_table_name(self):
        """测试获取隔离的表名"""
        table_name = self.isolator.get_table_name("tenant_123", "users")
        
        self.assertTrue(table_name.startswith("t_"))
        self.assertTrue(table_name.endswith("_users"))
        self.assertEqual(len(table_name), 8 + 1 + 8 + 1 + 5)  # t_ + hash + _ + users
    
    def test_get_schema_name(self):
        """测试获取schema名"""
        schema = self.isolator.get_schema_name("tenant_abc123")
        
        self.assertTrue(schema.startswith("tenant_"))
        self.assertEqual(len(schema), 7 + 12)  # tenant_ + 12 char hash
    
    def test_get_storage_path(self):
        """测试获取存储路径"""
        path = self.isolator.get_storage_path("tenant_123", "uploads", "images")
        
        self.assertTrue(path.exists())
        self.assertIn("tenant_123", str(path))
        self.assertIn("uploads", str(path))
        self.assertIn("images", str(path))
    
    def test_get_cache_key(self):
        """测试获取缓存键"""
        key = self.isolator.get_cache_key("tenant_123", "user:profile:456")
        
        self.assertEqual(key, "tenant:tenant_123:user:profile:456")
    
    def test_get_rate_limit_key(self):
        """测试获取限流键"""
        # 仅租户
        key1 = self.isolator.get_rate_limit_key("tenant_123")
        self.assertEqual(key1, "ratelimit:tenant_123")
        
        # 租户+用户
        key2 = self.isolator.get_rate_limit_key("tenant_123", "user_456")
        self.assertEqual(key2, "ratelimit:tenant_123:user_456")
    
    def test_get_log_prefix(self):
        """测试获取日志前缀"""
        prefix = self.isolator.get_log_prefix("tenant_1234567890abcdef")
        
        self.assertTrue(prefix.startswith("[Tenant:"))
        self.assertIn("tenant_123", prefix)
    
    def test_ensure_tenant_directory(self):
        """测试确保租户目录存在"""
        tenant_dir = self.isolator.ensure_tenant_directory("tenant_123")
        
        self.assertTrue(tenant_dir.exists())
        self.assertTrue((tenant_dir / "uploads").exists())
        self.assertTrue((tenant_dir / "exports").exists())
        self.assertTrue((tenant_dir / "temp").exists())
        self.assertTrue((tenant_dir / "data").exists())
    
    def test_cleanup_tenant_resources(self):
        """测试清理租户资源"""
        # 创建一些文件
        tenant_dir = self.isolator.ensure_tenant_directory("tenant_123")
        (tenant_dir / "test.txt").write_text("test content")
        
        # 清理
        result = self.isolator.cleanup_tenant_resources("tenant_123")
        self.assertTrue(result)
        
        # 验证已删除
        self.assertFalse(tenant_dir.exists())
    
    def test_list_tenant_resources(self):
        """测试列出租户资源"""
        # 空租户
        stats = self.isolator.list_tenant_resources("tenant_empty")
        self.assertEqual(stats["storage_used_bytes"], 0)
        self.assertEqual(stats["file_count"], 0)
        
        # 创建文件
        tenant_dir = self.isolator.ensure_tenant_directory("tenant_with_files")
        (tenant_dir / "file1.txt").write_text("content1")
        (tenant_dir / "file2.txt").write_text("content2" * 100)
        
        stats = self.isolator.list_tenant_resources("tenant_with_files")
        self.assertEqual(stats["file_count"], 2)
        self.assertGreater(stats["storage_used_bytes"], 0)
        self.assertGreater(stats["storage_used_mb"], 0)


class TestDatabaseRouter(unittest.TestCase):
    """测试数据库路由"""
    
    def setUp(self):
        """测试前准备"""
        self.router = DatabaseRouter(default_db="default")
    
    def test_db_for_read(self):
        """测试读取数据库路由"""
        db = self.router.db_for_read("tenant_123", "User")
        self.assertEqual(db, "default")
    
    def test_db_for_write(self):
        """测试写入数据库路由"""
        db = self.router.db_for_write("tenant_123", "User")
        self.assertEqual(db, "default")
    
    def test_allow_relation(self):
        """测试允许关联"""
        result = self.router.allow_relation(None, None)
        self.assertTrue(result)
    
    def test_allow_migrate(self):
        """测试允许迁移"""
        # 默认数据库允许迁移
        result = self.router.allow_migrate("tenant_123", "default", "auth")
        self.assertTrue(result)
        
        # 其他数据库不允许
        result = self.router.allow_migrate("tenant_123", "tenant_db", "auth")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
