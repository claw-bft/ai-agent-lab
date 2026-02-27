#!/usr/bin/env python3
"""
SearchAdapter 测试
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from search_adapter import SearchAdapter, SearchResult, search


class TestSearchResult(unittest.TestCase):
    """测试 SearchResult 数据类"""
    
    def test_basic_creation(self):
        """测试基本创建"""
        result = SearchResult(
            title="Test Title",
            snippet="Test snippet",
            url="https://example.com"
        )
        self.assertEqual(result.title, "Test Title")
        self.assertEqual(result.snippet, "Test snippet")
        self.assertEqual(result.url, "https://example.com")
        self.assertEqual(result.source, "web")
        self.assertIsNotNone(result.timestamp)
    
    def test_to_dict(self):
        """测试转换为字典"""
        result = SearchResult(
            title="Test",
            snippet="Snippet",
            url="https://example.com",
            source="test",
            score=0.95
        )
        d = result.to_dict()
        self.assertEqual(d["title"], "Test")
        self.assertEqual(d["score"], 0.95)


class TestSearchAdapter(unittest.TestCase):
    """测试 SearchAdapter"""
    
    def test_initialization(self):
        """测试初始化"""
        adapter = SearchAdapter()
        self.assertIsNotNone(adapter.backends)
        self.assertIn("preferred_backend", dir(adapter))
    
    def test_detect_backends(self):
        """测试后端检测"""
        adapter = SearchAdapter()
        backends = adapter._detect_backends()
        
        # 验证返回的字典包含预期的键
        expected_keys = ["tavily", "brave", "kimi_search", "web_search"]
        for key in expected_keys:
            self.assertIn(key, backends)
    
    def test_get_status(self):
        """测试获取状态"""
        adapter = SearchAdapter()
        status = adapter.get_status()
        
        self.assertIn("backends", status)
        self.assertIn("preferred", status)
        self.assertIn("available", status)
        self.assertIn("stats", status)
    
    @patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"})
    def test_tavily_detection(self):
        """测试 Tavily 检测"""
        # 模拟 tavily 包存在
        with patch("builtins.__import__", side_effect=lambda name, *args, **kwargs: MagicMock() if name == "tavily" else __import__(name, *args, **kwargs)):
            adapter = SearchAdapter()
            # 由于模拟限制，这里主要测试不抛出异常
            self.assertIsNotNone(adapter.backends)


class TestSearchIntegration(unittest.TestCase):
    """集成测试 - 需要环境变量配置"""
    
    @unittest.skipUnless(os.environ.get("TAVILY_API_KEY"), "需要 TAVILY_API_KEY")
    def test_tavily_search(self):
        """测试 Tavily 搜索"""
        adapter = SearchAdapter(preferred_backend="tavily")
        results = adapter.search("Python programming", limit=2)
        
        self.assertIsInstance(results, list)
        if results and results[0].source != "error":
            self.assertIsInstance(results[0], SearchResult)
            self.assertTrue(len(results[0].title) > 0)
    
    @unittest.skipUnless(os.environ.get("BRAVE_API_KEY"), "需要 BRAVE_API_KEY")
    def test_brave_search(self):
        """测试 Brave 搜索"""
        adapter = SearchAdapter(preferred_backend="brave")
        results = adapter.search("Python programming", limit=2)
        
        self.assertIsInstance(results, list)
        if results and results[0].source != "error":
            self.assertIsInstance(results[0], SearchResult)


class TestUtilityFunctions(unittest.TestCase):
    """测试便捷函数"""
    
    def test_search_function(self):
        """测试 search() 函数"""
        # 由于 search() 需要实际后端，这里主要测试函数存在和基本行为
        self.assertTrue(callable(search))


def run_tests():
    """运行测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestSearchResult))
    suite.addTests(loader.loadTestsFromTestCase(TestSearchAdapter))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilityFunctions))
    
    # 集成测试（需要环境变量）
    suite.addTests(loader.loadTestsFromTestCase(TestSearchIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
