"""
Stock Portfolio Analyzer 测试套件
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入带连字符的模块名
import importlib.util
spec = importlib.util.spec_from_file_location("stock_analyzer", 
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "stock-analyzer.py"))
stock_analyzer = importlib.util.module_from_spec(spec)
sys.modules["stock_analyzer"] = stock_analyzer
spec.loader.exec_module(stock_analyzer)

from stock_analyzer import (
    StockInfo, AnalysisReport,
    NewsAgent, StockAgent, ReportAgent, DeployAgent,
    StockAnalyzer
)


class TestStockInfo(unittest.TestCase):
    """StockInfo 数据类测试"""
    
    def test_stock_info_creation(self):
        """测试创建 StockInfo 对象"""
        stock = StockInfo(
            name="测试股票",
            symbol="TEST",
            price=100.0,
            news=[{"title": "测试新闻"}],
            technical={"rsi": 50},
            score=75,
            recommendation="买入"
        )
        
        self.assertEqual(stock.name, "测试股票")
        self.assertEqual(stock.symbol, "TEST")
        self.assertEqual(stock.price, 100.0)
        self.assertEqual(stock.score, 75)
        self.assertEqual(stock.recommendation, "买入")
    
    def test_stock_info_defaults(self):
        """测试 StockInfo 默认值"""
        stock = StockInfo(
            name="测试",
            symbol="TST",
            price=50.0
        )
        
        self.assertIsNone(stock.news)
        self.assertIsNone(stock.technical)
        self.assertEqual(stock.score, 0)
        self.assertEqual(stock.recommendation, "")


class TestAnalysisReport(unittest.TestCase):
    """AnalysisReport 数据类测试"""
    
    def test_report_creation(self):
        """测试创建 AnalysisReport"""
        stocks = [
            StockInfo(name="股票A", symbol="A", price=100.0),
            StockInfo(name="股票B", symbol="B", price=200.0)
        ]
        
        report = AnalysisReport(
            report_id="test-001",
            timestamp=datetime.now().isoformat(),
            stocks=stocks,
            summary={"total": 2, "average_score": 75},
            overall_recommendation="持有"
        )
        
        self.assertEqual(report.report_id, "test-001")
        self.assertEqual(len(report.stocks), 2)
        self.assertEqual(report.overall_recommendation, "持有")


class TestNewsAgent(unittest.TestCase):
    """NewsAgent 测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.agent = NewsAgent()
    
    def test_agent_initialization(self):
        """测试 Agent 初始化"""
        self.assertEqual(self.agent.name, "NewsAgent")
    
    def test_collect_news_structure(self):
        """测试新闻收集返回结构"""
        news = self.agent.collect_news("000001", "平安银行")
        
        self.assertIsInstance(news, list)
        self.assertGreater(len(news), 0)
        
        # 检查新闻项结构
        item = news[0]
        self.assertIn("title", item)
        self.assertIn("source", item)
        self.assertIn("sentiment", item)
        self.assertIn("impact", item)
    
    def test_collect_news_sentiment_values(self):
        """测试情感值有效性"""
        news = self.agent.collect_news("000001", "平安银行")
        
        valid_sentiments = ["positive", "negative", "neutral"]
        for item in news:
            self.assertIn(item.get("sentiment"), valid_sentiments)


class TestStockAgent(unittest.TestCase):
    """StockAgent 测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.agent = StockAgent()
    
    def test_agent_initialization(self):
        """测试 Agent 初始化"""
        self.assertEqual(self.agent.name, "StockAgent")
    
    def test_analyze_structure(self):
        """测试股票分析返回结构"""
        result = self.agent.analyze("000001", "平安银行")
        
        self.assertIn("symbol", result)
        self.assertIn("name", result)
        self.assertIn("score", result)
        self.assertIn("recommendation", result)
        self.assertIn("indicators", result)
    
    def test_calculate_technical_score(self):
        """测试技术评分计算"""
        quote = {"price": 100.0, "change": 1.5}
        history = {"trend": "up", "volatility": 0.02}
        
        score = self.agent._calculate_technical_score(quote, history)
        
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_generate_recommendation_high(self):
        """测试高评分推荐"""
        rec = self.agent._generate_recommendation(85, 2.0)
        self.assertIn("强烈", rec)
    
    def test_generate_recommendation_medium(self):
        """测试中评分推荐"""
        rec = self.agent._generate_recommendation(60, 0.5)
        self.assertIsInstance(rec, str)
        self.assertGreater(len(rec), 0)
    
    def test_generate_recommendation_low(self):
        """测试低评分推荐"""
        rec = self.agent._generate_recommendation(25, -2.0)
        self.assertIsInstance(rec, str)


class TestReportAgent(unittest.TestCase):
    """ReportAgent 测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.agent = ReportAgent()
    
    def test_agent_initialization(self):
        """测试 Agent 初始化"""
        self.assertEqual(self.agent.name, "ReportAgent")
    
    def test_generate_html_structure(self):
        """测试 HTML 报告生成结构"""
        stocks = [
            StockInfo(name="A", symbol="A", price=100.0, score=80, recommendation="买入"),
        ]
        
        report = AnalysisReport(
            report_id="test-001",
            timestamp=datetime.now().isoformat(),
            stocks=stocks,
            summary={"total_stocks": 1, "average_score": 80},
            overall_recommendation="积极配置"
        )
        
        html = self.agent.generate_html(report)
        
        self.assertIn("持仓分析报告", html)
        self.assertIn("A", html)
        self.assertIn("80", html)
        self.assertIn("<!DOCTYPE html>", html)


class TestDeployAgent(unittest.TestCase):
    """DeployAgent 测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.agent = DeployAgent()
    
    def test_agent_initialization(self):
        """测试 Agent 初始化"""
        self.assertEqual(self.agent.name, "DeployAgent")


class TestStockAnalyzer(unittest.TestCase):
    """StockAnalyzer 集成测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.analyzer = StockAnalyzer()
    
    def test_initialization(self):
        """测试分析器初始化"""
        self.assertIsNotNone(self.analyzer.news_agent)
        self.assertIsNotNone(self.analyzer.stock_agent)
        self.assertIsNotNone(self.analyzer.report_agent)
        self.assertIsNotNone(self.analyzer.deploy_agent)
    
    def test_parse_stocks_json(self):
        """测试JSON格式股票解析"""
        json_input = '[{"name": "平安银行", "symbol": "000001", "price": 10.5}]'
        stocks = self.analyzer.parse_stocks(json_input)
        
        self.assertEqual(len(stocks), 1)
        self.assertEqual(stocks[0].symbol, "000001")
        self.assertEqual(stocks[0].name, "平安银行")
    
    def test_parse_stocks_text_format(self):
        """测试文本格式股票解析"""
        text_input = "平安银行 - 000001 - 10.5"
        stocks = self.analyzer.parse_stocks(text_input)
        
        self.assertEqual(len(stocks), 1)
        self.assertEqual(stocks[0].symbol, "000001")
        self.assertEqual(stocks[0].price, 10.5)
    
    def test_parse_stocks_multiple_lines(self):
        """测试多行股票解析"""
        text_input = "平安银行 - 000001 - 10.5\n贵州茅台 - 600519 - 1500.0"
        stocks = self.analyzer.parse_stocks(text_input)
        
        self.assertEqual(len(stocks), 2)
    
    def test_analyze(self):
        """测试分析流程"""
        json_input = '[{"name": "平安银行", "symbol": "000001", "price": 10.5}]'
        report = self.analyzer.analyze(json_input)
        
        self.assertIsNotNone(report)
        self.assertIsInstance(report.report_id, str)
        self.assertEqual(len(report.stocks), 1)
        self.assertIn("total", report.summary)


class TestEdgeCases(unittest.TestCase):
    """边界情况测试"""
    
    def test_empty_input(self):
        """测试空输入"""
        analyzer = StockAnalyzer()
        stocks = analyzer.parse_stocks("")
        self.assertEqual(len(stocks), 0)
    
    def test_invalid_json(self):
        """测试无效JSON"""
        analyzer = StockAnalyzer()
        stocks = analyzer.parse_stocks("{invalid json}")
        # 应该返回空列表而不是崩溃
        self.assertIsInstance(stocks, list)
    
    def test_stock_with_zero_price(self):
        """测试价格为0的股票"""
        stock = StockInfo(name="测试", symbol="TST", price=0.0)
        self.assertEqual(stock.price, 0.0)
    
    def test_very_high_score(self):
        """测试极高评分"""
        agent = StockAgent()
        rec = agent._generate_recommendation(100, 5.0)
        self.assertIsInstance(rec, str)
        self.assertGreater(len(rec), 0)
    
    def test_very_low_score(self):
        """测试极低评分"""
        agent = StockAgent()
        rec = agent._generate_recommendation(0, -5.0)
        self.assertIsInstance(rec, str)
        self.assertGreater(len(rec), 0)


if __name__ == '__main__':
    unittest.main()
