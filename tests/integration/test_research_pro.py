"""
集成测试 - Research Pro
测试研究技能包的完整功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../skills/research-pro'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../skills/skill-cli'))

import pytest
from unittest.mock import Mock, patch

from research_pro import ResearchReport, WebSearchClient, DeepResearchEngine, DataAnalyzer
from data_adapter import ResearchDataAdapter, DataAdapterResult as DataResult


class TestResearchReport:
    """测试研究报告"""
    
    def test_creation(self):
        """测试创建研究报告"""
        report = ResearchReport(
            topic="AI发展趋势",
            summary="AI正在快速发展",
            key_findings=["发现1", "发现2"]
        )
        
        assert report.topic == "AI发展趋势"
        assert len(report.key_findings) == 2
        assert report.generated_at is not None


class TestWebSearchClient:
    """测试网页搜索客户端"""
    
    @pytest.fixture
    def client(self):
        """创建搜索客户端实例"""
        return WebSearchClient()
    
    def test_initialization(self, client):
        """测试初始化"""
        assert client is not None
        assert hasattr(client, 'brave_api_key')
    
    def test_search_with_mock(self, client):
        """测试搜索（使用mock）"""
        # 没有API key时使用mock
        client.brave_api_key = None
        client.tavily_api_key = None
        
        result = client.search("Python教程", count=5)
        
        assert isinstance(result, list)
        assert len(result) > 0


class TestDeepResearchEngine:
    """测试深度研究引擎"""
    
    @pytest.fixture
    def researcher(self):
        """创建深度研究引擎实例"""
        return DeepResearchEngine()
    
    def test_initialization(self, researcher):
        """测试初始化"""
        assert researcher is not None
    
    def test_research(self, researcher):
        """测试研究功能"""
        result = researcher.research("AI发展趋势", depth="basic")
        
        assert result is not None
        assert isinstance(result, ResearchReport)


class TestDataAnalyzer:
    """测试数据分析器"""
    
    @pytest.fixture
    def analyzer(self):
        """创建数据分析器实例"""
        return DataAnalyzer()
    
    def test_initialization(self, analyzer):
        """测试初始化"""
        assert analyzer is not None
    
    def test_analyze(self, analyzer):
        """测试分析功能"""
        test_data = [
            {"name": "A", "value": 10},
            {"name": "B", "value": 20},
            {"name": "C", "value": 30}
        ]
        result = analyzer.analyze(test_data, query="统计分析")
        
        assert result is not None
        assert isinstance(result, dict)


class TestResearchDataAdapter:
    """测试研究数据适配器"""
    
    @pytest.fixture
    def adapter(self):
        """创建适配器实例"""
        return ResearchDataAdapter()
    
    def test_initialization(self, adapter):
        """测试初始化"""
        assert adapter is not None
        assert hasattr(adapter, 'search_client')
    
    def test_deep_research(self, adapter):
        """测试深度研究"""
        result = adapter.deep_research("AI发展趋势", depth="comprehensive")
        
        assert isinstance(result, DataResult)
        assert result.success or result.error is not None
    
    def test_realtime_search(self, adapter):
        """测试实时搜索"""
        result = adapter.realtime_search("Python教程", sources=["news", "blog"])
        
        assert isinstance(result, DataResult)
    
    def test_search_with_empty_query(self, adapter):
        """测试空查询"""
        result = adapter.realtime_search("", sources=["news"])
        
        assert isinstance(result, DataResult)
    
    def test_mock_fallback(self, adapter):
        """测试mock回退"""
        # 强制使用mock
        adapter.config = {"search_api": "mock"}
        result = adapter.realtime_search("测试", sources=["news"])
        
        assert isinstance(result, DataResult)
        assert result.success is True
        assert result.source == "mock"
