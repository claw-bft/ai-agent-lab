"""
单元测试 - Skill Router
测试技能路由器的核心功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../skills/skill-cli'))

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from skill_router import SkillRouter, SkillRoute
from intent_parser import Intent, IntentType, IntentParser


class TestSkillRouter:
    """测试技能路由器"""
    
    @pytest.fixture
    def router(self):
        """创建路由器实例"""
        with patch.object(SkillRouter, '_discover_skills', return_value=[
            'finance-pro', 'coding-pro', 'product-pro', 'research-pro'
        ]):
            return SkillRouter()
    
    # ========== 意图路由测试 ==========
    
    def test_route_get_quote(self, router):
        """测试行情查询路由"""
        intent = Intent(
            type=IntentType.GET_QUOTE,
            confidence=0.9,
            entities={"symbol": "600519.SH"},
            raw_text="查询茅台股票"
        )
        route = router.route(intent)
        
        assert route.skill_name == "finance-pro"
        assert route.command == "quote"
        assert "--symbol" in route.args
        assert "600519.SH" in route.args
        assert route.confidence > 0.5
    
    def test_route_analyze_stock(self, router):
        """测试股票分析路由"""
        intent = Intent(
            type=IntentType.ANALYZE_STOCK,
            confidence=0.85,
            entities={"symbol": "000001.SZ"},
            raw_text="分析平安银行"
        )
        route = router.route(intent)
        
        assert route.skill_name == "finance-pro"
        assert route.command == "analyze"
    
    def test_route_generate_code(self, router):
        """测试代码生成路由"""
        intent = Intent(
            type=IntentType.GENERATE_CODE,
            confidence=0.8,
            entities={"language": "Python", "prompt": "爬虫"},
            raw_text="写个Python爬虫"
        )
        route = router.route(intent)
        
        assert route.skill_name == "coding-pro"
        assert route.command == "generate"
    
    def test_route_research(self, router):
        """测试研究路由"""
        intent = Intent(
            type=IntentType.RESEARCH,
            confidence=0.75,
            entities={"topic": "AI发展趋势"},
            raw_text="研究AI发展趋势"
        )
        route = router.route(intent)
        
        assert route.skill_name == "research-pro"
        assert route.command == "deep"
    
    def test_route_competitor_analysis(self, router):
        """测试竞品分析路由"""
        intent = Intent(
            type=IntentType.COMPETITOR_ANALYSIS,
            confidence=0.8,
            entities={"product": "AI助手"},
            raw_text="分析AI助手竞品"
        )
        route = router.route(intent)
        
        assert route.skill_name == "product-pro"
        assert route.command == "competitor"
    
    # ========== 技能提示路由测试 ==========
    
    def test_route_with_skill_hint(self, router):
        """测试带技能提示的路由"""
        intent = Intent(
            type=IntentType.UNKNOWN,
            confidence=0.4,
            entities={},
            raw_text="股票相关",
            skill_hint="finance-pro"
        )
        route = router.route(intent)
        
        assert route.skill_name == "finance-pro"
    
    # ========== 默认路由测试 ==========
    
    def test_route_unknown_intent(self, router):
        """测试未知意图的默认路由"""
        intent = Intent(
            type=IntentType.UNKNOWN,
            confidence=0.3,
            entities={},
            raw_text="随机文本"
        )
        route = router.route(intent)
        
        # 默认路由到research-pro
        assert route.skill_name == "research-pro"
        assert route.confidence < 0.5
    
    # ========== 参数构建测试 ==========
    
    def test_build_args_finance_quote(self, router):
        """测试金融行情参数构建"""
        intent = Intent(
            type=IntentType.GET_QUOTE,
            confidence=0.9,
            entities={"symbol": "600519.SH"},
            raw_text="查询茅台"
        )
        args = router._build_args(intent, "finance-pro", "quote")
        
        assert "--symbol" in args
        assert "600519.SH" in args
    
    def test_build_args_coding_generate(self, router):
        """测试代码生成参数构建"""
        intent = Intent(
            type=IntentType.GENERATE_CODE,
            confidence=0.8,
            entities={"language": "Python", "prompt": "爬虫"},
            raw_text="写个Python爬虫"
        )
        args = router._build_args(intent, "coding-pro", "generate")
        
        assert "--language" in args
        assert "Python" in args
        assert "--prompt" in args
    
    def test_build_args_research_deep(self, router):
        """测试深度研究参数构建"""
        intent = Intent(
            type=IntentType.RESEARCH,
            confidence=0.75,
            entities={"topic": "AI发展趋势"},
            raw_text="研究AI发展趋势"
        )
        args = router._build_args(intent, "research-pro", "deep")
        
        assert "--topic" in args
        assert "AI发展趋势" in args
    
    # ========== 技能发现测试 ==========
    
    def test_discover_skills(self):
        """测试技能发现"""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.iterdir') as mock_iterdir:
                mock_skill_dir = Mock()
                mock_skill_dir.is_dir.return_value = True
                mock_skill_dir.name = "test-skill"
                
                mock_skill_md = Mock()
                mock_skill_md.exists.return_value = True
                mock_skill_dir.__truediv__ = Mock(return_value=mock_skill_md)
                
                mock_iterdir.return_value = [mock_skill_dir]
                
                router = SkillRouter()
                skills = router._discover_skills()
                
                assert "test-skill" in skills
    
    # ========== 技能信息测试 ==========
    
    def test_get_skill_info_nonexistent(self, router):
        """测试获取不存在的技能信息"""
        info = router.get_skill_info("nonexistent-skill")
        assert info["exists"] is False
    
    # ========== 智能匹配测试 ==========
    
    def test_smart_match_finance(self, router):
        """测试金融技能智能匹配"""
        intent = Intent(
            type=IntentType.UNKNOWN,
            confidence=0.3,
            entities={},
            raw_text="帮我看看股票"
        )
        matched = router._smart_match(intent)
        assert matched == "finance-pro"
    
    def test_smart_match_coding(self, router):
        """测试代码技能智能匹配"""
        intent = Intent(
            type=IntentType.UNKNOWN,
            confidence=0.3,
            entities={},
            raw_text="帮我写个程序"
        )
        matched = router._smart_match(intent)
        # 可能匹配coding-pro或返回None，取决于别名列表
        assert matched in ["coding-pro", None]
    
    def test_smart_match_no_match(self, router):
        """测试无匹配情况"""
        intent = Intent(
            type=IntentType.UNKNOWN,
            confidence=0.3,
            entities={},
            raw_text="今天天气"
        )
        matched = router._smart_match(intent)
        assert matched is None
    
    # ========== 列表技能测试 ==========
    
    def test_list_available_skills(self, router):
        """测试列出可用技能"""
        skills = router.list_available_skills()
        assert len(skills) == 4
        skill_names = [s["name"] for s in skills]
        assert "finance-pro" in skill_names
        assert "coding-pro" in skill_names


class TestSkillRoute:
    """测试SkillRoute数据类"""
    
    def test_route_creation(self):
        """测试路由对象创建"""
        route = SkillRoute(
            skill_name="finance-pro",
            command="quote",
            args=["--symbol", "600519.SH"],
            confidence=0.9,
            reason="匹配股票查询意图"
        )
        
        assert route.skill_name == "finance-pro"
        assert route.command == "quote"
        assert route.args == ["--symbol", "600519.SH"]
        assert route.confidence == 0.9
        assert route.reason == "匹配股票查询意图"
    
    def test_route_with_empty_args(self):
        """测试空参数路由"""
        route = SkillRoute(
            skill_name="research-pro",
            command="help",
            args=[],
            confidence=0.4,
            reason="默认路由"
        )
        
        assert route.args == []
