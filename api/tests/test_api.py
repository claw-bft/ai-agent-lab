#!/usr/bin/env python3
"""
ClawHub Registry API 测试套件
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import json
from unittest.mock import Mock, MagicMock
from index import (
    handle_health, handle_list_skills, handle_get_skill,
    handle_categories, handle_stats, handle_publish,
    SKILLS_REGISTRY, CATEGORIES
)


class TestHealthEndpoint(unittest.TestCase):
    """测试健康检查端点"""
    
    def test_health_check(self):
        """测试健康检查返回正确格式"""
        status, body = handle_health()
        
        self.assertEqual(status, 200)
        data = json.loads(body)
        
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'clawhub-registry')
        self.assertIn('version', data)
        self.assertIn('timestamp', data)
        self.assertIn('skills_count', data)
        self.assertIn('categories_count', data)


class TestListSkillsEndpoint(unittest.TestCase):
    """测试技能列表端点"""
    
    def test_list_all_skills(self):
        """测试列出所有技能"""
        status, body = handle_list_skills({})
        data = json.loads(body)
        
        self.assertEqual(status, 200)
        self.assertIn('skills', data)
        self.assertIn('total', data)
        self.assertGreater(data['total'], 0)
    
    def test_list_with_tag_filter(self):
        """测试按标签过滤"""
        status, body = handle_list_skills({'tag': ['finance']})
        data = json.loads(body)
        
        self.assertEqual(status, 200)
        self.assertIn('filters', data)
        self.assertEqual(data['filters']['tag'], 'finance')
    
    def test_list_with_search(self):
        """测试搜索"""
        status, body = handle_list_skills({'q': ['finance']})
        data = json.loads(body)
        
        self.assertEqual(status, 200)
        self.assertIn('filters', data)
        self.assertEqual(data['filters']['search'], 'finance')
    
    def test_list_with_sort(self):
        """测试排序"""
        # 按下载量排序
        status, body = handle_list_skills({'sort': ['downloads']})
        data = json.loads(body)
        
        self.assertEqual(status, 200)
        skills = data['skills']
        if len(skills) > 1:
            self.assertGreaterEqual(
                skills[0].get('downloads', 0),
                skills[1].get('downloads', 0)
            )


class TestGetSkillEndpoint(unittest.TestCase):
    """测试获取单个技能端点"""
    
    def test_get_existing_skill(self):
        """测试获取存在的技能"""
        status, body = handle_get_skill('finance-pro')
        data = json.loads(body)
        
        self.assertEqual(status, 200)
        self.assertIn('skill', data)
        self.assertEqual(data['skill']['name'], 'finance-pro')
        self.assertIn('install_command', data)
    
    def test_get_nonexistent_skill(self):
        """测试获取不存在的技能"""
        status, body = handle_get_skill('nonexistent-skill')
        data = json.loads(body)
        
        self.assertEqual(status, 404)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Skill not found')


class TestCategoriesEndpoint(unittest.TestCase):
    """测试分类端点"""
    
    def test_get_categories(self):
        """测试获取分类列表"""
        status, body = handle_categories()
        data = json.loads(body)
        
        self.assertEqual(status, 200)
        self.assertIn('categories', data)
        
        categories = data['categories']
        self.assertIn('finance', categories)
        self.assertIn('coding', categories)


class TestStatsEndpoint(unittest.TestCase):
    """测试统计端点"""
    
    def test_get_stats(self):
        """测试获取统计信息"""
        status, body = handle_stats()
        data = json.loads(body)
        
        self.assertEqual(status, 200)
        self.assertIn('total_skills', data)
        self.assertIn('total_downloads', data)
        self.assertIn('average_rating', data)
        self.assertIn('total_categories', data)
        self.assertIn('top_skills', data)
    
    def test_stats_values(self):
        """测试统计值合理性"""
        status, body = handle_stats()
        data = json.loads(body)
        
        self.assertGreaterEqual(data['total_skills'], 0)
        self.assertGreaterEqual(data['total_downloads'], 0)
        self.assertGreaterEqual(data['average_rating'], 0)
        self.assertLessEqual(data['average_rating'], 5)
        self.assertGreaterEqual(data['total_categories'], 0)


class TestPublishEndpoint(unittest.TestCase):
    """测试发布端点"""
    
    def test_publish_new_skill(self):
        """测试发布新技能"""
        # 使用一个临时名称
        import uuid
        temp_name = f"test-skill-{uuid.uuid4().hex[:8]}"
        
        body = {
            'name': temp_name,
            'version': '1.0.0',
            'description': 'Test skill',
            'author': 'test',
            'tags': ['test']
        }
        
        status, response_body = handle_publish(body)
        data = json.loads(response_body)
        
        self.assertEqual(status, 201)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Skill published successfully')
        self.assertIn('skill', data)
        
        # 清理
        if temp_name in SKILLS_REGISTRY:
            del SKILLS_REGISTRY[temp_name]
    
    def test_publish_without_name(self):
        """测试发布缺少名称"""
        body = {'version': '1.0.0'}
        
        status, response_body = handle_publish(body)
        data = json.loads(response_body)
        
        self.assertEqual(status, 400)
        self.assertIn('error', data)
    
    def test_publish_duplicate(self):
        """测试发布重复技能"""
        body = {
            'name': 'finance-pro',  # 已存在的技能
            'version': '1.0.0'
        }
        
        status, response_body = handle_publish(body)
        data = json.loads(response_body)
        
        self.assertEqual(status, 409)
        self.assertIn('error', data)


class TestSkillDataStructure(unittest.TestCase):
    """测试技能数据结构"""
    
    def test_skill_has_required_fields(self):
        """测试技能有必需字段"""
        for skill_name, skill in SKILLS_REGISTRY.items():
            self.assertIn('name', skill)
            self.assertIn('version', skill)
            self.assertIn('description', skill)
            self.assertIn('author', skill)
            self.assertIn('tags', skill)
            self.assertIn('downloads', skill)
            self.assertIn('rating', skill)
    
    def test_category_has_required_fields(self):
        """测试分类有必需字段"""
        for cat_id, cat in CATEGORIES.items():
            self.assertIn('name', cat)
            self.assertIn('description', cat)
            self.assertIn('skills', cat)


if __name__ == '__main__':
    unittest.main()
