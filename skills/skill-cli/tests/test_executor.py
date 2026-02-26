#!/usr/bin/env python3
"""
AI执行引擎测试
"""

import sys
import unittest
from pathlib import Path

# 添加被测代码路径
sys.path.insert(0, str(Path(__file__).parent.parent / "skill-cli"))

from executor import (
    IntentParser, SkillRouter, SkillExecutor,
    ExecutionStatus, ParsedIntent
)


class TestIntentParser(unittest.TestCase):
    """测试意图解析器"""
    
    def setUp(self):
        self.parser = IntentParser()
    
    def test_parse_stock_quote(self):
        """测试股票行情解析"""
        command = "分析一下茅台股票"
        intent = self.parser.parse(command)
        
        self.assertEqual(intent.skill_name, "finance-pro")
        self.assertEqual(intent.action, "analyze")
        self.assertIn("symbol", intent.parameters)
        self.assertEqual(intent.parameters["symbol"], "600519.SH")
        self.assertGreater(intent.confidence, 0.5)
    
    def test_parse_stock_symbol(self):
        """测试股票代码解析"""
        command = "获取000001.SZ的行情"
        intent = self.parser.parse(command)
        
        self.assertEqual(intent.skill_name, "finance-pro")
        self.assertEqual(intent.action, "quote")
        self.assertEqual(intent.parameters.get("symbol"), "000001.SZ")
    
    def test_parse_code_generate(self):
        """测试代码生成解析"""
        command = "生成一个Python爬虫"
        intent = self.parser.parse(command)
        
        self.assertEqual(intent.skill_name, "coding-pro")
        self.assertEqual(intent.action, "generate")
    
    def test_parse_research(self):
        """测试研究解析"""
        command = "深度研究AI发展趋势"
        intent = self.parser.parse(command)
        
        self.assertEqual(intent.skill_name, "research-pro")
        self.assertEqual(intent.action, "deep")
    
    def test_parse_product(self):
        """测试产品解析"""
        command = "分析AI代码助手竞品"
        intent = self.parser.parse(command)
        
        self.assertEqual(intent.skill_name, "product-pro")
        self.assertEqual(intent.action, "competitor")


class TestSkillRouter(unittest.TestCase):
    """测试技能路由器"""
    
    def setUp(self):
        self.router = SkillRouter()
    
    def test_registered_handlers(self):
        """测试处理器注册"""
        skills = self.router.get_available_skills()
        expected = ["finance-pro", "coding-pro", "product-pro", "research-pro"]
        
        for skill in expected:
            self.assertIn(skill, skills)
    
    def test_route_to_handler(self):
        """测试路由到处理器"""
        intent = ParsedIntent(
            skill_name="finance-pro",
            action="quote",
            parameters={},
            confidence=0.9,
            raw_command="test"
        )
        
        handler = self.router.route(intent)
        self.assertIsNotNone(handler)
        self.assertTrue(handler.can_handle(intent))


class TestSkillExecutor(unittest.TestCase):
    """测试技能执行器"""
    
    def setUp(self):
        self.executor = SkillExecutor()
    
    def test_execute_natural_language(self):
        """测试自然语言执行"""
        result = self.executor.execute_natural_language("分析一下腾讯股票")
        
        self.assertEqual(result.status, ExecutionStatus.SUCCESS)
        self.assertEqual(result.skill_name, "finance-pro")
        self.assertIsNotNone(result.output)
        self.assertGreater(result.duration_ms, 0)
    
    def test_execute_direct(self):
        """测试直接执行"""
        result = self.executor.execute_direct(
            "finance-pro",
            "quote",
            {"symbol": "000001.SZ"}
        )
        
        self.assertEqual(result.status, ExecutionStatus.SUCCESS)
        self.assertEqual(result.skill_name, "finance-pro")
    
    def test_get_skill_help(self):
        """测试获取帮助"""
        help_text = self.executor.get_skill_help("finance-pro")
        
        self.assertIn("finance-pro", help_text)
        self.assertIn("quote", help_text)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        self.executor = SkillExecutor()
    
    def test_full_flow_finance(self):
        """测试金融技能完整流程"""
        commands = [
            "茅台股票行情",
            "分析一下000001.SZ",
            "查看腾讯财报"
        ]
        
        for cmd in commands:
            result = self.executor.execute_natural_language(cmd)
            self.assertEqual(result.status, ExecutionStatus.SUCCESS)
            self.assertEqual(result.skill_name, "finance-pro")
    
    def test_full_flow_coding(self):
        """测试编程技能完整流程"""
        commands = [
            "生成Python代码",
            "审查代码",
            "创建GitHub仓库"
        ]
        
        for cmd in commands:
            result = self.executor.execute_natural_language(cmd)
            self.assertEqual(result.status, ExecutionStatus.SUCCESS)
            self.assertEqual(result.skill_name, "coding-pro")


def run_tests():
    """运行测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestIntentParser))
    suite.addTests(loader.loadTestsFromTestCase(TestSkillRouter))
    suite.addTests(loader.loadTestsFromTestCase(TestSkillExecutor))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
