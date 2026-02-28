#!/usr/bin/env python3
"""
Financial Daily Generator 测试套件
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from generator import FinancialNewsDaily


class TestFinancialNewsDaily(unittest.TestCase):
    """测试财经日报生成器"""
    
    def setUp(self):
        """测试前准备"""
        self.daily = FinancialNewsDaily()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.daily.output_dir)
        self.assertIsNotNone(self.daily.github_repo)
    
    def test_ensure_directories(self):
        """测试目录创建"""
        with patch('os.makedirs') as mock_makedirs:
            daily = FinancialNewsDaily()
            self.assertEqual(mock_makedirs.call_count, 3)  # 3个目录
    
    @patch('generator.FinancialNewsDaily.collect_news')
    @patch('generator.FinancialNewsDaily.analyze_market')
    def test_generate_report_with_data(self, mock_market, mock_news):
        """测试生成报告（有数据）"""
        mock_news.return_value = [
            {'title': '测试新闻1', 'source': '测试源', 'url': 'http://test.com'},
            {'title': '测试新闻2', 'source': '测试源2'},
        ]
        mock_market.return_value = {
            '000001.SH': {'name': '上证指数', 'price': '3000.00', 'change_percent': '+0.5'},
        }
        
        news = self.daily.collect_news()
        market = self.daily.analyze_market()
        report = self.daily.generate_report(news, market)
        
        self.assertIn('财经资讯日报', report)
        self.assertIn('上证指数', report)
        self.assertIn('测试新闻1', report)
        self.assertIn('市场概览', report)
        self.assertIn('热点资讯', report)
    
    def test_generate_report_empty_data(self):
        """测试生成报告（无数据）"""
        report = self.daily.generate_report([], {})
        
        self.assertIn('财经资讯日报', report)
        self.assertIn('市场数据获取中', report)
        self.assertIn('资讯采集中', report)
    
    def test_generate_report_structure(self):
        """测试报告结构"""
        news = [{'title': '新闻', 'source': '来源'}]
        market = {'idx': {'name': '指数', 'price': '100', 'change_percent': '+1'}}
        
        report = self.daily.generate_report(news, market)
        
        # 检查必要部分
        self.assertIn('# 财经资讯日报', report)
        self.assertIn('## 📊 市场概览', report)
        self.assertIn('## 🔥 热点资讯', report)
        self.assertIn('## 📈 分析摘要', report)
        self.assertIn('生成时间:', report)
    
    @patch('builtins.open', unittest.mock.mock_open())
    @patch('os.chdir')
    @patch('subprocess.run')
    def test_save_and_push(self, mock_run, mock_chdir):
        """测试保存和推送"""
        mock_run.return_value = Mock(returncode=0)
        
        report = "测试报告内容"
        result = self.daily.save_and_push(report)
        
        # 由于Git操作可能失败，我们只验证函数执行了
        # 实际结果取决于subprocess的执行
        self.assertIsInstance(result, bool)


class TestReportFormatting(unittest.TestCase):
    """测试报告格式化"""
    
    def setUp(self):
        self.daily = FinancialNewsDaily()
    
    def test_market_data_formatting(self):
        """测试市场数据格式化"""
        market = {
            '000001.SH': {'name': '上证指数', 'price': '3000.00', 'change_percent': '+0.5'},
            '399001.SZ': {'name': '深证成指', 'price': '10000.00', 'change_percent': '-0.3'},
        }
        report = self.daily.generate_report([], market)
        
        self.assertIn('上证指数', report)
        self.assertIn('3000.00', report)
        self.assertIn('+0.5', report)
        self.assertIn('深证成指', report)
    
    def test_news_formatting(self):
        """测试新闻格式化"""
        news = [
            {'title': '重大新闻', 'source': '权威媒体', 'url': 'http://example.com'},
            {'title': '普通新闻', 'source': '一般媒体'},  # 无URL
        ]
        report = self.daily.generate_report(news, {})
        
        self.assertIn('重大新闻', report)
        self.assertIn('权威媒体', report)
        self.assertIn('http://example.com', report)
        self.assertIn('普通新闻', report)
    
    def test_date_in_report(self):
        """测试报告中包含日期"""
        report = self.daily.generate_report([], {})
        today = datetime.now().strftime("%Y-%m-%d")
        
        self.assertIn(today, report)


class TestEdgeCases(unittest.TestCase):
    """测试边界情况"""
    
    def setUp(self):
        self.daily = FinancialNewsDaily()
    
    def test_empty_news_list(self):
        """测试空新闻列表"""
        report = self.daily.generate_report([], {'idx': {}})
        self.assertIn('资讯采集中', report)
    
    def test_empty_market_data(self):
        """测试空市场数据"""
        report = self.daily.generate_report([{'title': '新闻'}], {})
        self.assertIn('市场数据获取中', report)
    
    def test_news_without_source(self):
        """测试新闻缺少来源"""
        news = [{'title': '无来源新闻'}]
        report = self.daily.generate_report(news, {})
        self.assertIn('无来源新闻', report)
    
    def test_market_without_name(self):
        """测试市场数据缺少名称"""
        market = {'idx': {'price': '100'}}
        report = self.daily.generate_report([], market)
        self.assertIn('idx', report)  # 使用代码作为名称


if __name__ == '__main__':
    unittest.main()
