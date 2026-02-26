"""
集成测试 - Product Pro
测试产品技能包的完整功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../skills/product-pro'))

import pytest
from unittest.mock import Mock, patch

# product-pro 文件名包含连字符，需要特殊导入
import importlib.util
spec = importlib.util.spec_from_file_location("product_pro", 
    os.path.join(os.path.dirname(__file__), '../../skills/product-pro/product-pro.py'))
product_pro_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(product_pro_module)

CompetitorAnalyzer = product_pro_module.CompetitorAnalyzer
PRDGenerator = product_pro_module.PRDGenerator
CompetitorInfo = product_pro_module.CompetitorInfo
PRDSection = product_pro_module.PRDSection

# UserStoryGenerator 不存在，使用 MarketResearcher 替代
MarketResearcher = product_pro_module.MarketResearcher


class TestCompetitorAnalyzer:
    """测试竞品分析器"""
    
    @pytest.fixture
    def analyzer(self):
        """创建竞品分析器实例"""
        return CompetitorAnalyzer()
    
    def test_initialization(self, analyzer):
        """测试初始化"""
        assert analyzer is not None
        assert hasattr(analyzer, 'analysis_framework')
    
    def test_analyze(self, analyzer):
        """测试竞品分析"""
        result = analyzer.analyze("AI助手", competitors=["ChatGPT", "Claude"])
        
        assert result is not None
        assert isinstance(result, dict)
        assert "product" in result
    
    def test_analyze_empty_product(self, analyzer):
        """测试空产品名竞品分析"""
        result = analyzer.analyze("")
        
        assert result is not None


class TestPRDGenerator:
    """测试PRD生成器"""
    
    @pytest.fixture
    def prd_generator(self):
        """创建PRD生成器实例"""
        return PRDGenerator()
    
    def test_initialization(self, prd_generator):
        """测试初始化"""
        assert prd_generator is not None
    
    def test_generate(self, prd_generator):
        """测试生成PRD"""
        result = prd_generator.generate(
            product_name="登录功能",
            template="standard"
        )
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_generate_with_sections(self, prd_generator):
        """测试生成带章节的PRD"""
        sections = [
            PRDSection(title="需求背景", content="用户需要登录"),
            PRDSection(title="功能描述", content="支持多种登录方式")
        ]
        result = prd_generator.generate(
            product_name="登录功能",
            sections=sections
        )
        
        assert result is not None


class TestMarketResearcher:
    """测试市场研究器"""
    
    @pytest.fixture
    def researcher(self):
        """创建市场研究器实例"""
        return MarketResearcher()
    
    def test_initialization(self, researcher):
        """测试初始化"""
        assert researcher is not None
    
    def test_research(self, researcher):
        """测试研究功能"""
        result = researcher.research("SaaS市场")
        
        assert result is not None
        assert isinstance(result, dict)


class TestCompetitorInfo:
    """测试竞品信息数据类"""
    
    def test_creation(self):
        """测试创建竞品信息"""
        info = CompetitorInfo(
            name="TestProduct",
            positioning="AI助手",
            strengths=["速度快", "准确率高"],
            weaknesses=["价格高"],
            target_users="企业用户",
            pricing="$10/月"
        )
        
        assert info.name == "TestProduct"
        assert len(info.strengths) == 2
        assert info.key_features == []


class TestPRDSection:
    """测试PRD章节数据类"""
    
    def test_creation(self):
        """测试创建PRD章节"""
        section = PRDSection(
            title="需求背景",
            content="用户反馈需要此功能"
        )
        
        assert section.title == "需求背景"
        assert section.subsections == []
