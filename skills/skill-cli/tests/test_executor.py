#!/usr/bin/env python3
"""
Test suite for skill-cli executor module
Tests the core execution engine functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import Mock, patch, MagicMock
from executor import (
    ExecutionStatus,
    ExecutionResult,
    ParsedIntent,
    IntentParser,
    SkillRouter,
    ContextManager,
    SkillExecutor,
    FinanceProHandler,
    CodingProHandler,
    ProductProHandler,
    ResearchProHandler
)


class TestExecutionResult(unittest.TestCase):
    """Test ExecutionResult dataclass"""
    
    def test_result_creation(self):
        """Test creating an ExecutionResult"""
        result = ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            skill_name="test-skill",
            command="test command",
            output={"data": "test"},
            error=None,
            duration_ms=100
        )
        
        self.assertEqual(result.status, ExecutionStatus.SUCCESS)
        self.assertEqual(result.skill_name, "test-skill")
        self.assertEqual(result.output, {"data": "test"})
        self.assertIsNone(result.error)
        self.assertEqual(result.duration_ms, 100)
    
    def test_result_with_error(self):
        """Test ExecutionResult with error"""
        result = ExecutionResult(
            status=ExecutionStatus.FAILED,
            skill_name="test-skill",
            command="test command",
            output=None,
            error="Something went wrong",
            duration_ms=50
        )
        
        self.assertEqual(result.status, ExecutionStatus.FAILED)
        self.assertEqual(result.error, "Something went wrong")


class TestParsedIntent(unittest.TestCase):
    """Test ParsedIntent dataclass"""
    
    def test_intent_creation(self):
        """Test creating a ParsedIntent"""
        intent = ParsedIntent(
            skill_name="finance-pro",
            action="quote",
            parameters={"symbol": "600519.SH"},
            confidence=0.95,
            raw_command="查询茅台股价"
        )
        
        self.assertEqual(intent.skill_name, "finance-pro")
        self.assertEqual(intent.action, "quote")
        self.assertEqual(intent.parameters["symbol"], "600519.SH")
        self.assertEqual(intent.confidence, 0.95)


class TestIntentParser(unittest.TestCase):
    """Test IntentParser functionality"""
    
    def setUp(self):
        self.parser = IntentParser()
    
    def test_detect_skill_finance(self):
        """Test detecting finance-pro skill"""
        intent = self.parser.parse("查询茅台股票行情")
        self.assertEqual(intent.skill_name, "finance-pro")
    
    def test_detect_skill_coding(self):
        """Test detecting coding-pro skill"""
        intent = self.parser.parse("生成一个Python函数")
        self.assertEqual(intent.skill_name, "coding-pro")
    
    def test_detect_skill_product(self):
        """Test detecting product-pro skill"""
        intent = self.parser.parse("分析竞品")
        self.assertEqual(intent.skill_name, "product-pro")
    
    def test_detect_skill_research(self):
        """Test detecting research-pro skill"""
        intent = self.parser.parse("深度研究AI趋势")
        self.assertEqual(intent.skill_name, "research-pro")
    
    def test_detect_action_quote(self):
        """Test detecting quote action"""
        intent = self.parser.parse("查询茅台股价")
        self.assertEqual(intent.action, "quote")
    
    def test_detect_action_analyze(self):
        """Test detecting analyze action"""
        intent = self.parser.parse("分析股票技术指标")
        self.assertEqual(intent.action, "analyze")
    
    def test_extract_stock_symbol(self):
        """Test extracting stock symbol"""
        intent = self.parser.parse("查询000001.SZ的行情")
        self.assertEqual(intent.parameters["symbol"], "000001.SZ")
    
    def test_extract_stock_name(self):
        """Test extracting stock name"""
        intent = self.parser.parse("分析一下茅台")
        self.assertEqual(intent.parameters["stock_name"], "茅台")
        self.assertEqual(intent.parameters["symbol"], "600519.SH")
    
    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        intent = self.parser.parse("查询茅台股价")
        self.assertGreater(intent.confidence, 0.5)


class TestSkillRouter(unittest.TestCase):
    """Test SkillRouter functionality"""
    
    def setUp(self):
        self.router = SkillRouter()
    
    def test_registered_handlers(self):
        """Test that all handlers are registered"""
        skills = self.router.get_available_skills()
        self.assertIn("finance-pro", skills)
        self.assertIn("coding-pro", skills)
        self.assertIn("product-pro", skills)
        self.assertIn("research-pro", skills)
    
    def test_route_to_handler(self):
        """Test routing to correct handler"""
        intent = ParsedIntent(
            skill_name="finance-pro",
            action="quote",
            parameters={},
            confidence=1.0,
            raw_command="test"
        )
        
        handler = self.router.route(intent)
        self.assertIsInstance(handler, FinanceProHandler)
    
    def test_route_unknown_skill(self):
        """Test routing unknown skill"""
        intent = ParsedIntent(
            skill_name="unknown-skill",
            action="test",
            parameters={},
            confidence=1.0,
            raw_command="test"
        )
        
        handler = self.router.route(intent)
        self.assertIsNone(handler)


class TestContextManager(unittest.TestCase):
    """Test ContextManager functionality"""
    
    def setUp(self):
        self.manager = ContextManager()
    
    def test_set_session(self):
        """Test setting session ID"""
        self.manager.set_session("test-session-123")
        context = self.manager.get_context()
        self.assertEqual(context["session_id"], "test-session-123")
    
    def test_add_history(self):
        """Test adding to history"""
        result = ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            skill_name="test",
            command="test",
            output={},
            duration_ms=0
        )
        
        self.manager.add_history("test command", result)
        context = self.manager.get_context()
        self.assertEqual(len(context["history"]), 1)
    
    def test_history_limit(self):
        """Test history limit of 10 items"""
        for i in range(15):
            result = ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                skill_name="test",
                command=f"test {i}",
                output={},
                duration_ms=0
            )
            self.manager.add_history(f"test {i}", result)
        
        context = self.manager.get_context()
        self.assertEqual(len(context["history"]), 10)
    
    def test_variables(self):
        """Test variable storage"""
        self.manager.set_variable("key1", "value1")
        self.assertEqual(self.manager.get_variable("key1"), "value1")
        self.assertIsNone(self.manager.get_variable("nonexistent"))


class TestFinanceProHandler(unittest.TestCase):
    """Test FinanceProHandler"""
    
    def setUp(self):
        self.handler = FinanceProHandler()
    
    def test_can_handle(self):
        """Test can_handle method"""
        intent = ParsedIntent(
            skill_name="finance-pro",
            action="quote",
            parameters={},
            confidence=1.0,
            raw_command="test"
        )
        self.assertTrue(self.handler.can_handle(intent))
        
        intent.skill_name = "coding-pro"
        self.assertFalse(self.handler.can_handle(intent))
    
    @patch.object(FinanceProHandler, '_get_adapter')
    def test_execute_quote(self, mock_get_adapter):
        """Test execute quote action"""
        mock_adapter = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.data = {"price": 100}
        mock_result.error = None
        mock_result.latency_ms = 100
        mock_adapter.get_stock_quote.return_value = mock_result
        mock_get_adapter.return_value = mock_adapter
        
        intent = ParsedIntent(
            skill_name="finance-pro",
            action="quote",
            parameters={"symbol": "600519.SH"},
            confidence=1.0,
            raw_command="查询茅台"
        )
        
        result = self.handler.execute(intent)
        self.assertEqual(result.status, ExecutionStatus.SUCCESS)
        self.assertEqual(result.output["price"], 100)


class TestCodingProHandler(unittest.TestCase):
    """Test CodingProHandler"""
    
    def setUp(self):
        self.handler = CodingProHandler()
    
    def test_can_handle(self):
        """Test can_handle method"""
        intent = ParsedIntent(
            skill_name="coding-pro",
            action="generate",
            parameters={},
            confidence=1.0,
            raw_command="test"
        )
        self.assertTrue(self.handler.can_handle(intent))
    
    def test_execute_generate(self):
        """Test execute generate action"""
        intent = ParsedIntent(
            skill_name="coding-pro",
            action="generate",
            parameters={"prompt": "生成一个Python函数"},
            confidence=1.0,
            raw_command="生成一个Python函数"
        )
        
        result = self.handler.execute(intent)
        self.assertEqual(result.status, ExecutionStatus.SUCCESS)
        self.assertEqual(result.output["action"], "code_generate")
    
    def test_execute_review(self):
        """Test execute review action"""
        intent = ParsedIntent(
            skill_name="coding-pro",
            action="review",
            parameters={"path": "./src"},
            confidence=1.0,
            raw_command="审查代码"
        )
        
        result = self.handler.execute(intent)
        self.assertEqual(result.status, ExecutionStatus.SUCCESS)
        self.assertEqual(result.output["action"], "code_review")


class TestProductProHandler(unittest.TestCase):
    """Test ProductProHandler"""
    
    def setUp(self):
        self.handler = ProductProHandler()
    
    def test_execute_competitor(self):
        """Test execute competitor action"""
        intent = ParsedIntent(
            skill_name="product-pro",
            action="competitor",
            parameters={"product": "AI助手"},
            confidence=1.0,
            raw_command="分析竞品"
        )
        
        result = self.handler.execute(intent)
        self.assertEqual(result.status, ExecutionStatus.SUCCESS)
        self.assertEqual(result.output["action"], "competitor_analysis")
    
    def test_execute_prd(self):
        """Test execute prd action"""
        intent = ParsedIntent(
            skill_name="product-pro",
            action="prd",
            parameters={"feature": "登录功能"},
            confidence=1.0,
            raw_command="生成PRD"
        )
        
        result = self.handler.execute(intent)
        self.assertEqual(result.status, ExecutionStatus.SUCCESS)
        self.assertEqual(result.output["action"], "prd_create")


class TestResearchProHandler(unittest.TestCase):
    """Test ResearchProHandler"""
    
    def setUp(self):
        self.handler = ResearchProHandler()
    
    @patch.object(ResearchProHandler, '_get_adapter')
    def test_execute_deep(self, mock_get_adapter):
        """Test execute deep research action"""
        mock_adapter = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.data = {"research": "AI trends"}
        mock_result.error = None
        mock_result.latency_ms = 200
        mock_adapter.deep_research.return_value = mock_result
        mock_get_adapter.return_value = mock_adapter
        
        intent = ParsedIntent(
            skill_name="research-pro",
            action="deep",
            parameters={"topic": "AI发展趋势"},
            confidence=1.0,
            raw_command="深度研究AI"
        )
        
        result = self.handler.execute(intent)
        self.assertEqual(result.status, ExecutionStatus.SUCCESS)


class TestSkillExecutor(unittest.TestCase):
    """Test SkillExecutor main class"""
    
    def setUp(self):
        self.executor = SkillExecutor()
    
    @patch.object(FinanceProHandler, '_get_adapter')
    def test_execute_natural_language(self, mock_get_adapter):
        """Test executing natural language command"""
        mock_adapter = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.data = {"price": 100}
        mock_result.error = None
        mock_result.latency_ms = 100
        mock_adapter.get_stock_quote.return_value = mock_result
        mock_get_adapter.return_value = mock_adapter
        
        result = self.executor.execute_natural_language("查询茅台股价")
        self.assertEqual(result.status, ExecutionStatus.SUCCESS)
        self.assertEqual(result.skill_name, "finance-pro")
    
    def test_execute_direct(self):
        """Test direct execution"""
        result = self.executor.execute_direct(
            "coding-pro",
            "generate",
            {"prompt": "test"}
        )
        self.assertEqual(result.status, ExecutionStatus.SUCCESS)
        self.assertEqual(result.skill_name, "coding-pro")
    
    def test_get_skill_help(self):
        """Test getting skill help"""
        help_text = self.executor.get_skill_help("finance-pro")
        self.assertIn("finance-pro", help_text)
        self.assertIn("quote", help_text)
    
    def test_get_all_skills_help(self):
        """Test getting all skills help"""
        help_text = self.executor.get_skill_help()
        self.assertIn("finance-pro", help_text)
        self.assertIn("coding-pro", help_text)
        self.assertIn("product-pro", help_text)
        self.assertIn("research-pro", help_text)


class TestExecutionStatus(unittest.TestCase):
    """Test ExecutionStatus enum"""
    
    def test_status_values(self):
        """Test status enum values"""
        self.assertEqual(ExecutionStatus.SUCCESS.value, "success")
        self.assertEqual(ExecutionStatus.FAILED.value, "failed")
        self.assertEqual(ExecutionStatus.PARTIAL.value, "partial")
        self.assertEqual(ExecutionStatus.PENDING.value, "pending")


def run_tests():
    """Run all tests and return results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestExecutionResult,
        TestParsedIntent,
        TestIntentParser,
        TestSkillRouter,
        TestContextManager,
        TestFinanceProHandler,
        TestCodingProHandler,
        TestProductProHandler,
        TestResearchProHandler,
        TestSkillExecutor,
        TestExecutionStatus
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
