"""
认证模块测试
"""

import unittest
from datetime import datetime, timedelta

import sys
sys.path.insert(0, '/root/.openclaw/workspace/ai-agent-lab/multi-tenant')

from auth.auth import PasswordHasher, AuthManager, PermissionChecker, AuthToken


class TestPasswordHasher(unittest.TestCase):
    """测试密码哈希器"""
    
    def test_hash_password(self):
        """测试密码哈希"""
        password = "secure_password123"
        hashed = PasswordHasher.hash_password(password)
        
        # 哈希应包含盐值和哈希值
        self.assertIn("$", hashed)
        self.assertEqual(len(hashed.split("$")), 2)
    
    def test_verify_password_correct(self):
        """测试正确密码验证"""
        password = "secure_password123"
        hashed = PasswordHasher.hash_password(password)
        
        self.assertTrue(PasswordHasher.verify_password(password, hashed))
    
    def test_verify_password_incorrect(self):
        """测试错误密码验证"""
        password = "secure_password123"
        hashed = PasswordHasher.hash_password(password)
        
        self.assertFalse(PasswordHasher.verify_password("wrong_password", hashed))
    
    def test_verify_password_invalid_format(self):
        """测试无效格式哈希"""
        self.assertFalse(PasswordHasher.verify_password("password", "invalid_hash"))


class TestAuthManager(unittest.TestCase):
    """测试认证管理器"""
    
    def setUp(self):
        """测试前准备"""
        self.auth = AuthManager(token_expiry_hours=1)
    
    def test_set_and_verify_password(self):
        """测试设置和验证密码"""
        user_id = "user_123"
        password = "secure_password"
        
        self.auth.set_password(user_id, password)
        
        self.assertTrue(self.auth.verify_user_password(user_id, password))
        self.assertFalse(self.auth.verify_user_password(user_id, "wrong_password"))
    
    def test_generate_token(self):
        """测试生成令牌"""
        user_id = "user_123"
        tenant_id = "tenant_456"
        
        token = self.auth.generate_token(user_id, tenant_id)
        
        self.assertIsNotNone(token.access_token)
        self.assertIsNotNone(token.refresh_token)
        self.assertEqual(token.token_type, "Bearer")
        self.assertFalse(token.is_expired())
    
    def test_validate_token(self):
        """测试验证令牌"""
        user_id = "user_123"
        tenant_id = "tenant_456"
        
        token = self.auth.generate_token(user_id, tenant_id)
        validated = self.auth.validate_token(token.access_token)
        
        self.assertIsNotNone(validated)
        self.assertEqual(validated["user_id"], user_id)
    
    def test_validate_invalid_token(self):
        """测试验证无效令牌"""
        validated = self.auth.validate_token("invalid_token")
        self.assertIsNone(validated)
    
    def test_revoke_token(self):
        """测试撤销令牌"""
        user_id = "user_123"
        tenant_id = "tenant_456"
        
        token = self.auth.generate_token(user_id, tenant_id)
        
        # 撤销前有效
        self.assertIsNotNone(self.auth.validate_token(token.access_token))
        
        # 撤销
        result = self.auth.revoke_token(token.access_token)
        self.assertTrue(result)
        
        # 撤销后无效
        self.assertIsNone(self.auth.validate_token(token.access_token))
    
    def test_revoke_all_user_tokens(self):
        """测试撤销用户所有令牌"""
        user_id = "user_123"
        tenant_id = "tenant_456"
        
        # 生成多个令牌
        token1 = self.auth.generate_token(user_id, tenant_id)
        token2 = self.auth.generate_token(user_id, tenant_id)
        
        # 撤销所有
        count = self.auth.revoke_all_user_tokens(user_id)
        self.assertEqual(count, 2)
        
        # 都无效了
        self.assertIsNone(self.auth.validate_token(token1.access_token))
        self.assertIsNone(self.auth.validate_token(token2.access_token))


class TestPermissionChecker(unittest.TestCase):
    """测试权限检查器"""
    
    def test_check_permission(self):
        """测试权限检查"""
        # 有权限
        self.assertTrue(PermissionChecker.check(["user:read"], "user:read"))
        
        # 无权限
        self.assertFalse(PermissionChecker.check(["user:read"], "user:write"))
    
    def test_admin_permission(self):
        """测试管理员权限"""
        # 管理员有所有权限
        self.assertTrue(PermissionChecker.check(["tenant:admin"], "user:read"))
        self.assertTrue(PermissionChecker.check(["tenant:admin"], "skill:write"))
        self.assertTrue(PermissionChecker.check(["tenant:admin"], "billing:write"))
    
    def test_get_role_permissions(self):
        """测试获取角色权限"""
        owner_perms = PermissionChecker.get_role_permissions("owner")
        self.assertIn("user:read", owner_perms)
        self.assertIn("tenant:admin", owner_perms)
        
        admin_perms = PermissionChecker.get_role_permissions("admin")
        self.assertIn("user:write", admin_perms)
        
        member_perms = PermissionChecker.get_role_permissions("member")
        self.assertIn("skill:write", member_perms)
        
        viewer_perms = PermissionChecker.get_role_permissions("viewer")
        self.assertIn("skill:read", viewer_perms)
        self.assertNotIn("skill:write", viewer_perms)


if __name__ == "__main__":
    unittest.main()
