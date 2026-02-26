"""
单元测试 - Executor
测试执行引擎的核心功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../skills/skill-cli'))

import pytest
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass

from executor import (
    SkillExecutor, IntentParser, SkillRouter, ContextManager,
    ExecutionStatus, ExecutionResult, ParsedIntent,
    FinanceProHandler, CodingProHandler, ProductProHandler, ResearchProHandler
)


class MockAdapter:
    """模拟数据适配器"""
    def __init__(self, success=True, data=None, error=None):
        self.success = success
        self.data = data or {"mock": "data"}
        self.error = error
        self.latency_ms = 100
        self.source = "mock"  # 添加source属性
    
    def get_stock_quote(self, symbol):
        return self
    
    def technical_analysis(self, symbol, indicators):
        return self
    
    def get_financial_report(self, symbol):
        return self
    
    def get_stock_history(self, symbol, period):
        return self
    
    def deep_research(self, topic, depth):
        return self
    
    def realtime_search(self, query, sources):
        return self


class TestExecutionStatus:
    """测试执行状态枚举"""
    
    def test_status_values(self):
        """测试状态值"""
        assert ExecutionStatus.SUCCESS.value == "success"
        assert ExecutionStatus.PARTIAL.value == "partial"
        assert ExecutionStatus.FAILED.value == "failed"
        assert ExecutionStatus.PENDING.value == "pending"


class TestExecutionResult:
    """测试执行结果"""
    
    def test_result_creation(self):
        """测试结果对象创建"""
        result = ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            skill_name="finance-pro",
            command="查询茅台",
            output={"price": 1800.0},
            error=None,
            duration_ms=150,
            metadata={"source": "akshare"}
        )
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.skill_name == "finance-pro"
        assert result.output["price"] == 1800.0
        assert result.duration_ms == 150


class TestParsedIntent:
    """测试解析后的意图"""
    
    def test_intent_creation(self):
        """测试意图对象创建"""
        intent = ParsedIntent(
            skill_name="finance-pro",
            action="quote",
            parameters={"symbol": "600519.SH"},
            confidence=0.9,
            raw_command="查询茅台股票"
        )
        
        assert intent.skill_name == "finance-pro"
        assert intent.action == "quote"
        assert intent.parameters["symbol"] == "600519.SH"
        assert intent.confidence == 0.9


class TestContextManager:
    """测试上下文管理器"""
    
    @pytest.fixture
    def context(self):
        """创建上下文实例"""
        return ContextManager()
    
    def test_initial_state(self, context):
        """测试初始状态"""
        ctx = context.get_context()
        assert ctx["session_id"] is None
        assert ctx["history"] == []
        assert ctx["variables"] == {}
    
    def test_set_session(self, context):
        """测试设置会话"""
        context.set_session("session-123")
        assert context.get_context()["session_id"] == "session-123"
    
    def test_add_history(self, context):
        """测试添加历史记录"""
        result = ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            skill_name="finance-pro",
            command="查询茅台",
            output={},
            duration_ms=100
        )
        context.add_history("查询茅台", result)
        
        ctx = context.get_context()
        assert len(ctx["history"]) == 1
        assert ctx["history"][0]["command"] == "查询茅台"
    
    def test_history_limit(self, context):
        """测试历史记录限制"""
        for i in range(15):
            result = ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                skill_name="finance-pro",
                command=f"命令{i}",
                output={},
                duration_ms=100
            )
            context.add_history(f"命令{i}", result)
        
        ctx = context.get_context()
        assert len(ctx["history"]) == 10  # 只保留最近10条
    
    def test_set_and_get_variable(self, context):
        """测试变量设置和获取"""
        context.set_variable("symbol", "600519.SH")
        assert context.get_variable("symbol") == "600519.SH"
    
    def test_get_nonexistent_variable(self, context):
        """测试获取不存在的变量"""
        assert context.get_variable("nonexistent") is None


class TestFinanceProHandler:
    """测试金融处理器"""
    
    @pytest.fixture
    def handler(self):
        """创建处理器实例"""
        return FinanceProHandler()
    
    def test_can_handle(self, handler):
        """测试能否处理意图"""
        intent = ParsedIntent(
            skill_name="finance-pro",
            action="quote",
            parameters={},
            confidence=0.9,
            raw_command="查询茅台"
        )
        assert handler.can_handle(intent) is True
    
    def test_cannot_handle_other_skill(self, handler):
        """测试不能处理其他技能"""
        intent = ParsedIntent(
            skill_name="coding-pro",
            action="generate",
            parameters={},
            confidence=0.9,
            raw_command="写代码"
        )
        assert handler.can_handle(intent) is False
    
    @patch('executor.FinanceProHandler._get_adapter')
    def test_execute_quote(self, mock_get_adapter, handler):
        """测试执行行情查询"""
        mock_adapter = MockAdapter(success=True, data={"price": 1800.0})
        mock_get_adapter.return_value = mock_adapter
        
        intent = ParsedIntent(
            skill_name="finance-pro",
            action="quote",
            parameters={"symbol": "600519.SH"},
            confidence=0.9,
            raw_command="查询茅台"
        )
        
        result = handler.execute(intent)
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.skill_name == "finance-pro"
        assert result.output is not None
    
    @patch('executor.FinanceProHandler._get_adapter')
    def test_execute_analyze(self, mock_get_adapter, handler):
        """测试执行技术分析"""
        mock_adapter = MockAdapter(success=True, data={"rsi": 65.5})
        mock_get_adapter.return_value = mock_adapter
        
        intent = ParsedIntent(
            skill_name="finance-pro",
            action="analyze",
            parameters={"symbol": "600519.SH"},
            confidence=0.9,
            raw_command="分析茅台"
        )
        
        result = handler.execute(intent)
        
        assert result.status == ExecutionStatus.SUCCESS
    
    def test_execute_unknown_action(self, handler):
        """测试执行未知动作"""
        intent = ParsedIntent(
            skill_name="finance-pro",
            action="unknown_action",
            parameters={},
            confidence=0.9,
            raw_command="未知命令"
        )
        
        result = handler.execute(intent)
        
        assert result.status == ExecutionStatus.FAILED
        assert "未知动作" in result.error
    
    def test_get_help(self, handler):
        """测试获取帮助"""
        help_text = handler.get_help()
        assert "finance-pro" in help_text
        assert "quote" in help_text
        assert "analyze" in help_text


class TestCodingProHandler:
    """测试代码处理器"""
    
    @pytest.fixture
    def handler(self):
        """创建处理器实例"""
        return CodingProHandler()
    
    def test_can_handle(self, handler):
        """测试能否处理意图"""
        intent = ParsedIntent(
            skill_name="coding-pro",
            action="generate",
            parameters={},
            confidence=0.9,
            raw_command="写代码"
        )
        assert handler.can_handle(intent) is True
    
    def test_execute_generate(self, handler):
        """测试执行代码生成"""
        intent = ParsedIntent(
            skill_name="coding-pro",
            action="generate",
            parameters={"prompt": "爬虫", "language": "Python"},
            confidence=0.9,
            raw_command="写个Python爬虫"
        )
        
        result = handler.execute(intent)
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.output["action"] == "code_generate"
        assert result.output["prompt"] == "爬虫"
    
    def test_execute_review(self, handler):
        """测试执行代码审查"""
        intent = ParsedIntent(
            skill_name="coding-pro",
            action="review",
            parameters={"path": "./src"},
            confidence=0.9,
            raw_command="审查代码"
        )
        
        result = handler.execute(intent)
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.output["action"] == "code_review"


class TestProductProHandler:
    """测试产品处理器"""
    
    @pytest.fixture
    def handler(self):
        """创建处理器实例"""
        return ProductProHandler()
    
    def test_execute_competitor(self, handler):
        """测试执行竞品分析"""
        intent = ParsedIntent(
            skill_name="product-pro",
            action="competitor",
            parameters={"product": "AI助手"},
            confidence=0.9,
            raw_command="分析竞品"
        )
        
        result = handler.execute(intent)
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.output["action"] == "competitor_analysis"
    
    def test_execute_prd(self, handler):
        """测试执行PRD创建"""
        intent = ParsedIntent(
            skill_name="product-pro",
            action="prd",
            parameters={"feature": "登录功能"},
            confidence=0.9,
            raw_command="写PRD"
        )
        
        result = handler.execute(intent)
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.output["action"] == "prd_create"


class TestResearchProHandler:
    """测试研究处理器"""
    
    @pytest.fixture
    def handler(self):
        """创建处理器实例"""
        return ResearchProHandler()
    
    @patch('executor.ResearchProHandler._get_adapter')
    def test_execute_deep(self, mock_get_adapter, handler):
        """测试执行深度研究"""
        mock_adapter = MockAdapter(success=True, data={"summary": "AI趋势..."})
        mock_get_adapter.return_value = mock_adapter
        
        intent = ParsedIntent(
            skill_name="research-pro",
            action="deep",
            parameters={"topic": "AI发展趋势"},
            confidence=0.9,
            raw_command="研究AI"
        )
        
        result = handler.execute(intent)
        
        assert result.status == ExecutionStatus.SUCCESS
    
    @patch('executor.ResearchProHandler._get_adapter')
    def test_execute_search(self, mock_get_adapter, handler):
        """测试执行搜索"""
        mock_adapter = MockAdapter(success=True, data={"results": []})
        mock_get_adapter.return_value = mock_adapter
        
        intent = ParsedIntent(
            skill_name="research-pro",
            action="search",
            parameters={"query": "最新科技新闻"},
            confidence=0.9,
            raw_command="搜索新闻"
        )
        
        result = handler.execute(intent)
        
        assert result.status == ExecutionStatus.SUCCESS


class TestSkillExecutor:
    """测试技能执行器"""
    
    @pytest.fixture
    def executor(self):
        """创建执行器实例"""
        return SkillExecutor()
    
    def test_initialization(self, executor):
        """测试初始化"""
        assert executor.intent_parser is not None
        assert executor.skill_router is not None
        assert executor.context_manager is not None
    
    @patch.object(IntentParser, 'parse')
    @patch.object(SkillRouter, 'route')
    def test_execute_natural_language(self, mock_route, mock_parse, executor):
        """测试执行自然语言命令"""
        # 设置mock
        mock_parse.return_value = ParsedIntent(
            skill_name="finance-pro",
            action="quote",
            parameters={"symbol": "600519.SH"},
            confidence=0.9,
            raw_command="查询茅台"
        )
        
        mock_handler = Mock()
        mock_handler.can_handle.return_value = True
        mock_handler.execute.return_value = ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            skill_name="finance-pro",
            command="查询茅台",
            output={"price": 1800.0},
            duration_ms=100
        )
        mock_route.return_value = mock_handler
        
        result = executor.execute_natural_language("查询茅台")
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.skill_name == "finance-pro"
    
    @patch.object(IntentParser, 'parse')
    @patch.object(SkillRouter, 'route')
    def test_execute_no_handler(self, mock_route, mock_parse, executor):
        """测试无处理器情况"""
        mock_parse.return_value = ParsedIntent(
            skill_name="unknown-skill",
            action="unknown",
            parameters={},
            confidence=0.3,
            raw_command="未知命令"
        )
        mock_route.return_value = None
        
        result = executor.execute_natural_language("未知命令")
        
        assert result.status == ExecutionStatus.FAILED
        assert "未找到技能处理器" in result.error
    
    @patch.object(SkillRouter, 'route')
    def test_execute_direct(self, mock_route, executor):
        """测试直接执行"""
        mock_handler = Mock()
        mock_handler.can_handle.return_value = True
        mock_handler.execute.return_value = ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            skill_name="finance-pro",
            command="quote",
            output={},
            duration_ms=100
        )
        mock_route.return_value = mock_handler
        
        result = executor.execute_direct("finance-pro", "quote", {"symbol": "600519.SH"})
        
        assert result.status == ExecutionStatus.SUCCESS
    
    def test_get_skill_help(self, executor):
        """测试获取技能帮助"""
        help_text = executor.get_skill_help()
        assert "finance-pro" in help_text
        assert "coding-pro" in help_text
