#!/usr/bin/env python3
"""
搜索适配器测试
验证多后端搜索功能
"""

import sys
import os
import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from search_adapter import SearchAdapter, search, batch_search


class TestSearchAdapter(unittest.TestCase):
    """测试搜索适配器"""
    
    def setUp(self):
        self.adapter = SearchAdapter()
    
    def test_init_detects_backends(self):
        """测试初始化时检测后端"""
        self.assertIsInstance(self.adapter.backends, dict)
        self.assertIn("kimi_search", self.adapter.backends)
        self.assertIn("web_search", self.adapter.backends)
        self.assertIn("tavily", self.adapter.backends)
    
    def test_select_backend_priority(self):
        """测试后端选择优先级"""
        # 模拟所有后端都可用
        self.adapter.backends = {
            "kimi_search": True,
            "web_search": True,
            "tavily": True
        }
        selected = self.adapter._select_backend()
        self.assertEqual(selected, "kimi_search")  # 最高优先级
    
    def test_select_backend_fallback(self):
        """测试后端选择回退"""
        # 模拟只有web_search可用
        self.adapter.backends = {
            "kimi_search": False,
            "web_search": True,
            "tavily": False
        }
        selected = self.adapter._select_backend()
        self.assertEqual(selected, "web_search")
    
    def test_select_backend_none(self):
        """测试无可用后端"""
        self.adapter.backends = {
            "kimi_search": False,
            "web_search": False,
            "tavily": False
        }
        selected = self.adapter._select_backend()
        self.assertEqual(selected, "none")
    
    def test_mock_search_returns_result(self):
        """测试模拟搜索返回结果"""
        results = self.adapter._mock_search("测试查询")
        self.assertEqual(len(results), 1)
        self.assertIn("测试查询", results[0]["title"])
        self.assertEqual(results[0]["source"], "mock")
    
    def test_search_with_no_backend(self):
        """测试无后端时的搜索行为"""
        self.adapter.preferred_backend = "none"
        results = self.adapter.search("查询")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["source"], "mock")
    
    def test_batch_search(self):
        """测试批量搜索"""
        queries = ["查询1", "查询2", "查询3"]
        results = self.adapter.batch_search(queries, limit=2)
        
        self.assertIsInstance(results, dict)
        self.assertEqual(len(results), 3)
        for query in queries:
            self.assertIn(query, results)
            self.assertIsInstance(results[query], list)
    
    def test_deduplicate_results(self):
        """测试结果去重"""
        results = [
            {"title": "A", "url": "http://a.com", "snippet": "..."},
            {"title": "B", "url": "http://a.com", "snippet": "..."},  # 重复URL
            {"title": "C", "url": "http://b.com", "snippet": "..."},
            {"title": "D", "url": "", "snippet": "..."},  # 空URL
        ]
        unique = self.adapter.deduplicate_results(results, key="url")
        self.assertEqual(len(unique), 3)  # 去重后应为3条
    
    def test_aggregate_results(self):
        """测试聚合结果"""
        batch_results = {
            "查询1": [
                {"title": "A", "url": "http://a.com"},
                {"title": "B", "url": "http://b.com"}
            ],
            "查询2": [
                {"title": "C", "url": "http://c.com"},
                {"title": "A", "url": "http://a.com"}  # 重复
            ]
        }
        aggregated = self.adapter.aggregate_results(batch_results)
        self.assertEqual(len(aggregated), 3)  # 去重后3条
    
    def test_get_status(self):
        """测试获取状态"""
        status = self.adapter.get_status()
        self.assertIsInstance(status, dict)
        self.assertIn("backends", status)
        self.assertIn("preferred", status)
        self.assertIn("available", status)


class TestNormalization(unittest.TestCase):
    """测试结果标准化"""
    
    def setUp(self):
        self.adapter = SearchAdapter()
    
    def test_normalize_kimi_results(self):
        """测试kimi结果标准化"""
        raw_results = [
            {"title": "标题", "snippet": "摘要", "url": "http://example.com", "source": "news"},
            {"title": "标题2", "content": "内容", "link": "http://test.com"}  # 不同字段名
        ]
        normalized = self.adapter._normalize_kimi_results(raw_results)
        
        self.assertEqual(len(normalized), 2)
        for r in normalized:
            self.assertIn("title", r)
            self.assertIn("snippet", r)
            self.assertIn("url", r)
            self.assertIn("timestamp", r)
    
    def test_normalize_web_results(self):
        """测试web结果标准化"""
        raw_results = [
            {"title": "标题", "description": "描述", "link": "http://example.com"}
        ]
        normalized = self.adapter._normalize_web_results(raw_results)
        
        self.assertEqual(len(normalized), 1)
        self.assertEqual(normalized[0]["title"], "标题")
        self.assertEqual(normalized[0]["snippet"], "描述")
        self.assertEqual(normalized[0]["url"], "http://example.com")
    
    def test_normalize_tavily_results(self):
        """测试tavily结果标准化"""
        raw_results = [
            {"title": "标题", "content": "内容", "url": "http://example.com", "score": 0.95}
        ]
        normalized = self.adapter._normalize_tavily_results(raw_results)
        
        self.assertEqual(len(normalized), 1)
        self.assertEqual(normalized[0]["title"], "标题")
        self.assertEqual(normalized[0]["snippet"], "内容")
        self.assertEqual(normalized[0]["score"], 0.95)


class TestConvenienceFunctions(unittest.TestCase):
    """测试便捷函数"""
    
    def test_search_function(self):
        """测试search便捷函数"""
        results = search("测试", limit=2)
        self.assertIsInstance(results, list)
    
    def test_batch_search_function(self):
        """测试batch_search便捷函数"""
        results = batch_search(["查询1", "查询2"], limit=2)
        self.assertIsInstance(results, dict)
        self.assertIn("查询1", results)
        self.assertIn("查询2", results)


class TestErrorHandling(unittest.TestCase):
    """测试错误处理"""
    
    def setUp(self):
        self.adapter = SearchAdapter()
    
    @patch('subprocess.run')
    def test_search_kimi_error(self, mock_run):
        """测试kimi搜索错误处理"""
        mock_run.return_value = Mock(returncode=1, stderr="Error")
        self.adapter.preferred_backend = "kimi_search"
        
        results = self.adapter._search_kimi("查询", 5)
        self.assertEqual(len(results), 1)
        self.assertIn("error", results[0])
    
    @patch('subprocess.run')
    def test_search_kimi_exception(self, mock_run):
        """测试kimi搜索异常处理"""
        mock_run.side_effect = Exception("Network error")
        self.adapter.preferred_backend = "kimi_search"
        
        results = self.adapter._search_kimi("查询", 5)
        self.assertEqual(len(results), 1)
        self.assertIn("error", results[0])
        self.assertIn("Network error", results[0]["error"])


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestSearchAdapter))
    suite.addTests(loader.loadTestsFromTestCase(TestNormalization))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
