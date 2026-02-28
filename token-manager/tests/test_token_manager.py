"""
Token Manager 测试套件
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from datetime import datetime

from token_manager import TokenManager, get_token, set_token


class TestTokenManager(unittest.TestCase):
    """TokenManager 核心功能测试"""
    
    def setUp(self):
        """每个测试前创建临时凭证文件"""
        self.temp_dir = tempfile.mkdtemp()
        self.tokens_file = Path(self.temp_dir) / 'test_tokens.json'
        self.tm = TokenManager(str(self.tokens_file))
    
    def tearDown(self):
        """每个测试后清理临时文件"""
        if self.tokens_file.exists():
            self.tokens_file.unlink()
        os.rmdir(self.temp_dir)
    
    def test_init_creates_empty_storage(self):
        """测试初始化创建空存储"""
        self.assertEqual(self.tm.list_services(), [])
        self.assertFalse(self.tm.has_token('nonexistent'))
    
    def test_set_and_get_token(self):
        """测试设置和获取凭证"""
        self.tm.set_token('github', 'ghp_xxx123', username='testuser')
        
        # 获取完整对象
        data = self.tm.get_token('github')
        self.assertIsNotNone(data)
        self.assertEqual(data['token'], 'ghp_xxx123')
        self.assertEqual(data['username'], 'testuser')
        self.assertIn('created_at', data)
        
        # 获取特定字段
        token = self.tm.get_token('github', 'token')
        self.assertEqual(token, 'ghp_xxx123')
        
        username = self.tm.get_token('github', 'username')
        self.assertEqual(username, 'testuser')
    
    def test_get_nonexistent_token(self):
        """测试获取不存在的凭证"""
        self.assertIsNone(self.tm.get_token('nonexistent'))
        self.assertIsNone(self.tm.get_token('nonexistent', 'token'))
    
    def test_update_token(self):
        """测试更新凭证"""
        self.tm.set_token('github', 'old_token', note='old note')
        
        result = self.tm.update_token('github', token='new_token', note='new note')
        self.assertTrue(result)
        
        data = self.tm.get_token('github')
        self.assertEqual(data['token'], 'new_token')
        self.assertEqual(data['note'], 'new note')
        self.assertIn('updated_at', data)
    
    def test_update_nonexistent_token(self):
        """测试更新不存在的凭证"""
        result = self.tm.update_token('nonexistent', token='xxx')
        self.assertFalse(result)
    
    def test_delete_token(self):
        """测试删除凭证"""
        self.tm.set_token('github', 'token123')
        self.assertTrue(self.tm.has_token('github'))
        
        result = self.tm.delete_token('github')
        self.assertTrue(result)
        self.assertFalse(self.tm.has_token('github'))
    
    def test_delete_nonexistent_token(self):
        """测试删除不存在的凭证"""
        result = self.tm.delete_token('nonexistent')
        self.assertFalse(result)
    
    def test_list_services(self):
        """测试列出所有服务"""
        self.tm.set_token('github', 'token1')
        self.tm.set_token('vercel', 'token2')
        self.tm.set_token('aws', 'token3')
        
        services = self.tm.list_services()
        self.assertEqual(len(services), 3)
        self.assertIn('github', services)
        self.assertIn('vercel', services)
        self.assertIn('aws', services)
    
    def test_get_all_tokens_hides_secrets(self):
        """测试获取所有凭证时隐藏敏感信息"""
        self.tm.set_token('github', 'secret_token', username='user')
        
        all_tokens = self.tm.get_all_tokens()
        self.assertEqual(all_tokens['github']['token'], '***')
        self.assertEqual(all_tokens['github']['username'], 'user')
    
    def test_export_tokens(self):
        """测试导出凭证"""
        self.tm.set_token('github', 'secret123')
        
        # 不包含敏感信息
        export_no_secret = self.tm.export_tokens(include_secrets=False)
        self.assertEqual(export_no_secret['github']['token'], '***')
        
        # 包含敏感信息
        export_with_secret = self.tm.export_tokens(include_secrets=True)
        self.assertEqual(export_with_secret['github']['token'], 'secret123')
    
    def test_import_tokens_merge(self):
        """测试导入凭证（合并模式）"""
        self.tm.set_token('existing', 'token1')
        
        new_tokens = {
            'new_service': {'token': 'token2', 'created_at': '2026-01-01'},
            'existing': {'token': 'updated_token', 'created_at': '2026-02-01'}
        }
        
        self.tm.import_tokens(new_tokens, merge=True)
        
        # 保留旧服务
        self.assertTrue(self.tm.has_token('new_service'))
        # 更新现有服务
        self.assertEqual(self.tm.get_token('existing', 'token'), 'updated_token')
    
    def test_import_tokens_replace(self):
        """测试导入凭证（覆盖模式）"""
        self.tm.set_token('old_service', 'token1')
        
        new_tokens = {
            'new_service': {'token': 'token2', 'created_at': '2026-01-01'}
        }
        
        self.tm.import_tokens(new_tokens, merge=False)
        
        # 旧服务被删除
        self.assertFalse(self.tm.has_token('old_service'))
        # 新服务存在
        self.assertTrue(self.tm.has_token('new_service'))
    
    def test_persistence(self):
        """测试凭证持久化到文件"""
        # 创建并保存凭证
        self.tm.set_token('github', 'persistent_token', note='test')
        
        # 创建新的管理器实例读取同一文件
        tm2 = TokenManager(str(self.tokens_file))
        
        data = tm2.get_token('github')
        self.assertEqual(data['token'], 'persistent_token')
        self.assertEqual(data['note'], 'test')
    
    def test_clear_all(self):
        """测试清除所有凭证"""
        self.tm.set_token('service1', 'token1')
        self.tm.set_token('service2', 'token2')
        
        self.tm.clear_all()
        
        self.assertEqual(self.tm.list_services(), [])
        self.assertFalse(self.tm.has_token('service1'))
        self.assertFalse(self.tm.has_token('service2'))


class TestConvenienceFunctions(unittest.TestCase):
    """便捷函数测试"""
    
    def setUp(self):
        """创建临时凭证文件"""
        self.temp_dir = tempfile.mkdtemp()
        self.tokens_file = Path(self.temp_dir) / 'test_tokens.json'
    
    def tearDown(self):
        """清理临时文件"""
        if self.tokens_file.exists():
            self.tokens_file.unlink()
        os.rmdir(self.temp_dir)
    
    def test_get_token_convenience(self):
        """测试便捷获取函数"""
        # 先设置凭证
        set_token('test_service', 'my_token', 
                  tokens_file=str(self.tokens_file),
                  username='testuser')
        
        # 使用便捷函数获取
        token = get_token('test_service', 'token', str(self.tokens_file))
        self.assertEqual(token, 'my_token')
        
        username = get_token('test_service', 'username', str(self.tokens_file))
        self.assertEqual(username, 'testuser')
    
    def test_set_token_convenience(self):
        """测试便捷设置函数"""
        set_token('github', 'ghp_xxx', 
                  tokens_file=str(self.tokens_file),
                  scopes=['repo', 'user'])
        
        # 验证设置成功
        tm = TokenManager(str(self.tokens_file))
        self.assertTrue(tm.has_token('github'))
        self.assertEqual(tm.get_token('github', 'token'), 'ghp_xxx')


class TestEdgeCases(unittest.TestCase):
    """边界情况测试"""
    
    def setUp(self):
        """创建临时凭证文件"""
        self.temp_dir = tempfile.mkdtemp()
        self.tokens_file = Path(self.temp_dir) / 'test_tokens.json'
        self.tm = TokenManager(str(self.tokens_file))
    
    def tearDown(self):
        """清理临时文件"""
        if self.tokens_file.exists():
            self.tokens_file.unlink()
        os.rmdir(self.temp_dir)
    
    def test_empty_token_value(self):
        """测试空token值"""
        self.tm.set_token('empty_service', '')
        self.assertEqual(self.tm.get_token('empty_service', 'token'), '')
    
    def test_special_characters_in_service_name(self):
        """测试特殊字符服务名"""
        special_names = ['my-service', 'my_service', 'my.service', '123service']
        for name in special_names:
            self.tm.set_token(name, f'token_{name}')
            self.assertTrue(self.tm.has_token(name))
    
    def test_unicode_metadata(self):
        """测试Unicode元数据"""
        self.tm.set_token('github', 'token123', 
                         note='中文备注',
                         description='日本語テスト',
                         emoji='🚀')
        
        data = self.tm.get_token('github')
        self.assertEqual(data['note'], '中文备注')
        self.assertEqual(data['description'], '日本語テスト')
        self.assertEqual(data['emoji'], '🚀')
    
    def test_large_token_value(self):
        """测试大token值"""
        large_token = 'x' * 10000
        self.tm.set_token('large', large_token)
        self.assertEqual(self.tm.get_token('large', 'token'), large_token)
    
    def test_corrupted_file_handling(self):
        """测试损坏文件处理"""
        # 写入损坏的JSON
        self.tokens_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tokens_file, 'w') as f:
            f.write('not valid json')
        
        # 应该能正常初始化，使用空存储
        tm = TokenManager(str(self.tokens_file))
        self.assertEqual(tm.list_services(), [])


if __name__ == '__main__':
    unittest.main()
