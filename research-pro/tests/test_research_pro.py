#!/usr/bin/env python3
"""
Research Pro 测试套件
验证搜索、研究、分析、监控功能
"""

import sys
import os
import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from research_pro import (
    WebSearchClient, DeepResearchEngine, DataAnalyzer, CompetitorMonitor,
    SearchResult, ResearchReport, search, deep_research, analyze_data, monitor_competitors
)


class TestWebSearchClient(unittest.TestCase):
    """测试搜索客户端"""
    
    def setUp(self):
        self.client = WebSearchClient()
    
    def test_mock_search_returns_results(self):
        """测试模拟搜索返回结果"""
        results = self.client._mock_search("测试查询", 3)
        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], SearchResult)
        self.assertIn("测试查询", results[0].title)
    
    def test_search_returns_list(self):
        """测试搜索返回列表"""
        results = self.client.search("AI技术", count=3)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
    
    def test_search_result_structure(self):
        """测试结果结构正确"""
        results = self.client.search("测试", count=1)
        if results:
            result = results[0]
            self.assertTrue(hasattr(result, 'title'))
            self.assertTrue(hasattr(result, 'url'))
            self.assertTrue(hasattr(result, 'snippet'))


class TestDeepResearchEngine(unittest.TestCase):
    """测试深度研究引擎"""
    
    def setUp(self):
        self.engine = DeepResearchEngine()
    
    def test_generate_queries_basic(self):
        """测试基础查询生成"""
        queries = self.engine._generate_queries("新能源汽车", "quick")
        self.assertEqual(len(queries), 1)
        self.assertEqual(queries[0], "新能源汽车")
    
    def test_generate_queries_standard(self):
        """测试标准查询生成"""
        queries = self.engine._generate_queries("新能源汽车", "standard")
        self.assertEqual(len(queries), 4)
        self.assertIn("新能源汽车", queries)
        self.assertIn("新能源汽车 最新趋势", queries)
    
    def test_generate_queries_comprehensive(self):
        """测试全面查询生成"""
        queries = self.engine._generate_queries("新能源汽车", "comprehensive")
        self.assertEqual(len(queries), 8)
        self.assertIn("新能源汽车 技术发展", queries)
        self.assertIn("新能源汽车 竞争格局", queries)
    
    def test_deduplicate_results(self):
        """测试结果去重"""
        results = [
            SearchResult("标题1", "http://a.com", "摘要1", "source"),
            SearchResult("标题2", "http://a.com", "摘要2", "source"),  # 重复URL
            SearchResult("标题3", "http://b.com", "摘要3", "source"),
        ]
        unique = self.engine._deduplicate_results(results)
        self.assertEqual(len(unique), 2)
    
    def test_research_returns_report(self):
        """测试研究返回报告"""
        report = self.engine.research("AI编程工具", depth="quick")
        self.assertIsInstance(report, ResearchReport)
        self.assertEqual(report.topic, "AI编程工具")
        self.assertTrue(hasattr(report, 'summary'))
        self.assertTrue(hasattr(report, 'key_findings'))


class TestDataAnalyzer(unittest.TestCase):
    """测试数据分析器"""
    
    def setUp(self):
        self.analyzer = DataAnalyzer()
    
    def test_analyze_nonexistent_file(self):
        """测试分析不存在的文件"""
        result = self.analyzer.analyze_file("/nonexistent/file.csv", "查询")
        self.assertIn("error", result)
    
    def test_analyze_unsupported_format(self):
        """测试不支持的文件格式"""
        # 创建一个临时txt文件
        test_file = Path("/tmp/test_research.txt")
        test_file.write_text("test content")
        try:
            result = self.analyzer.analyze_file(str(test_file), "查询")
            self.assertIn("error", result)
            self.assertIn("不支持的文件格式", result["error"])
        finally:
            test_file.unlink()


class TestCompetitorMonitor(unittest.TestCase):
    """测试竞品监控器"""
    
    def setUp(self):
        self.monitor = CompetitorMonitor()
    
    def test_build_monitor_query(self):
        """测试监控查询构建"""
        query = self.monitor._build_monitor_query("OpenAI", "product-launch")
        self.assertIn("OpenAI", query)
        self.assertIn("发布", query)
    
    def test_build_monitor_query_funding(self):
        """测试融资类查询构建"""
        query = self.monitor._build_monitor_query("Anthropic", "funding")
        self.assertIn("Anthropic", query)
        self.assertIn("融资", query)
    
    def test_monitor_returns_dict(self):
        """测试监控返回字典"""
        result = self.monitor.monitor(["TestCorp"], ["news"])
        self.assertIsInstance(result, dict)
        self.assertIn("monitored_competitors", result)
        self.assertIn("alerts", result)


class TestPublicAPI(unittest.TestCase):
    """测试公共API函数"""
    
    def test_search_function(self):
        """测试search函数"""
        results = search("人工智能", count=2)
        self.assertIsInstance(results, list)
        if results:
            self.assertIn("title", results[0])
            self.assertIn("url", results[0])
    
    def test_deep_research_function(self):
        """测试deep_research函数"""
        result = deep_research("机器学习", depth="quick")
        self.assertIsInstance(result, dict)
        self.assertIn("topic", result)
        self.assertIn("summary", result)
        self.assertIn("key_findings", result)
        self.assertEqual(result["topic"], "机器学习")
    
    def test_analyze_data_nonexistent(self):
        """测试analyze_data处理不存在的文件"""
        result = analyze_data("/nonexistent/data.csv", "统计")
        self.assertIn("error", result)
    
    def test_monitor_competitors_function(self):
        """测试monitor_competitors函数"""
        result = monitor_competitors(["CompanyA", "CompanyB"], ["news"])
        self.assertIsInstance(result, dict)
        self.assertIn("monitored_competitors", result)
        self.assertEqual(len(result["monitored_competitors"]), 2)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_end_to_end_research(self):
        """测试端到端研究流程"""
        # 执行深度研究
        report = deep_research("区块链应用", depth="quick")
        
        # 验证报告结构
        self.assertIn("topic", report)
        self.assertIn("summary", report)
        self.assertIn("sources_count", report)
        self.assertIn("sources", report)
        
        # 验证数据来源
        self.assertIsInstance(report["sources"], list)
        self.assertGreaterEqual(report["sources_count"], 0)
    
    def test_search_to_analysis_flow(self):
        """测试搜索到分析的流程"""
        # 搜索
        search_results = search("Python编程", count=3)
        self.assertIsInstance(search_results, list)
        
        # 验证可以序列化
        json_str = json.dumps(search_results, ensure_ascii=False)
        self.assertIsInstance(json_str, str)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestWebSearchClient))
    suite.addTests(loader.loadTestsFromTestCase(TestDeepResearchEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestDataAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestCompetitorMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestPublicAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
