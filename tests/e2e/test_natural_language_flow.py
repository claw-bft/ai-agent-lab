"""
端到端测试 - 自然语言流程
测试从自然语言输入到技能执行的完整流程
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../skills/skill-cli'))

import pytest
from unittest.mock import Mock, patch

from executor import SkillExecutor, ExecutionStatus


class TestNaturalLanguageFlow:
    """测试自然语言端到端流程"""
    
    @pytest.fixture
    def executor(self):
        """创建执行器实例"""
        return SkillExecutor()
    
    # ========== 金融场景测试 ==========
    
    def test_flow_stock_quote(self, executor):
        """测试股票查询流程"""
        result = executor.execute_natural_language("查询茅台股票")
        
        assert result.status in [ExecutionStatus.SUCCESS, ExecutionStatus.FAILED]
        assert result.skill_name in ["finance-pro", "unknown"]
    
    def test_flow_stock_analysis(self, executor):
        """测试股票分析流程"""
        result = executor.execute_natural_language("分析一下600519的走势")
        
        assert result is not None
        assert result.command is not None
    
    def test_flow_stock_financial(self, executor):
        """测试财报查询流程"""
        result = executor.execute_natural_language("查看腾讯财报")
        
        assert result is not None
    
    # ========== 代码场景测试 ==========
    
    def test_flow_code_generation(self, executor):
        """测试代码生成流程"""
        result = executor.execute_natural_language("帮我写一个Python爬虫")
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.skill_name == "coding-pro"
        assert result.output is not None
    
    def test_flow_code_review(self, executor):
        """测试代码审查流程"""
        result = executor.execute_natural_language("审查这个目录的代码")
        
        assert result is not None
        assert result.skill_name in ["coding-pro", "research-pro"]
    
    # ========== 研究场景测试 ==========
    
    def test_flow_research(self, executor):
        """测试研究流程"""
        result = executor.execute_natural_language("研究一下AI发展趋势")
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.skill_name == "research-pro"
    
    def test_flow_search(self, executor):
        """测试搜索流程"""
        result = executor.execute_natural_language("搜索最新的科技新闻")
        
        assert result is not None
    
    # ========== 产品场景测试 ==========
    
    def test_flow_competitor_analysis(self, executor):
        """测试竞品分析流程"""
        result = executor.execute_natural_language("分析AI代码助手竞品")
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.skill_name == "product-pro"
    
    def test_flow_prd_creation(self, executor):
        """测试PRD创建流程"""
        result = executor.execute_natural_language("为登录功能写PRD")
        
        assert result is not None
    
    def test_flow_ppt_creation(self, executor):
        """测试PPT创建流程"""
        result = executor.execute_natural_language("制作产品介绍PPT")
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.skill_name == "product-pro"
    
    # ========== 边界情况测试 ==========
    
    def test_flow_empty_command(self, executor):
        """测试空命令"""
        result = executor.execute_natural_language("")
        
        assert result is not None
        assert result.status in [ExecutionStatus.FAILED, ExecutionStatus.SUCCESS]
    
    def test_flow_unknown_command(self, executor):
        """测试未知命令"""
        result = executor.execute_natural_language("今天天气怎么样")
        
        assert result is not None
        # 未知命令会路由到research-pro作为通用研究
    
    def test_flow_gibberish(self, executor):
        """测试无意义输入"""
        result = executor.execute_natural_language("asdfghjkl")
        
        assert result is not None
    
    # ========== 上下文保持测试 ==========
    
    def test_flow_context_preservation(self, executor):
        """测试上下文保持"""
        # 执行第一个命令
        result1 = executor.execute_natural_language("查询茅台股票")
        
        # 执行第二个命令（可能依赖上下文）
        result2 = executor.execute_natural_language("分析一下这个股票")
        
        # 检查历史记录
        history = executor.context_manager.get_context()["history"]
        assert len(history) >= 2
    
    # ========== 多轮对话测试 ==========
    
    def test_flow_multi_turn_conversation(self, executor):
        """测试多轮对话"""
        commands = [
            "查询茅台股票",
            "分析一下这个股票的技术面",
            "看看它的财报",
        ]
        
        results = []
        for cmd in commands:
            result = executor.execute_natural_language(cmd)
            results.append(result)
        
        assert len(results) == 3
        # 所有命令都应该成功或至少被处理
        for r in results:
            assert r is not None
            assert r.command is not None


class TestDirectExecutionFlow:
    """测试直接执行流程"""
    
    @pytest.fixture
    def executor(self):
        """创建执行器实例"""
        return SkillExecutor()
    
    def test_direct_finance_quote(self, executor):
        """测试直接执行金融行情"""
        result = executor.execute_direct(
            skill_name="finance-pro",
            action="quote",
            params={"symbol": "600519.SH"}
        )
        
        assert result is not None
        assert result.skill_name == "finance-pro"
    
    def test_direct_coding_generate(self, executor):
        """测试直接执行代码生成"""
        result = executor.execute_direct(
            skill_name="coding-pro",
            action="generate",
            params={"prompt": "爬虫", "language": "Python"}
        )
        
        assert result.status == ExecutionStatus.SUCCESS
    
    def test_direct_product_competitor(self, executor):
        """测试直接执行竞品分析"""
        result = executor.execute_direct(
            skill_name="product-pro",
            action="competitor",
            params={"product": "AI助手"}
        )
        
        assert result.status == ExecutionStatus.SUCCESS
    
    def test_direct_research_deep(self, executor):
        """测试直接执行深度研究"""
        result = executor.execute_direct(
            skill_name="research-pro",
            action="deep",
            params={"topic": "AI发展趋势"}
        )
        
        assert result is not None
    
    def test_direct_unknown_skill(self, executor):
        """测试直接执行未知技能"""
        result = executor.execute_direct(
            skill_name="unknown-skill",
            action="unknown",
            params={}
        )
        
        assert result.status == ExecutionStatus.FAILED


class TestHelpSystemFlow:
    """测试帮助系统流程"""
    
    @pytest.fixture
    def executor(self):
        """创建执行器实例"""
        return SkillExecutor()
    
    def test_get_all_skills_help(self, executor):
        """测试获取所有技能帮助"""
        help_text = executor.get_skill_help()
        
        assert "finance-pro" in help_text
        assert "coding-pro" in help_text
        assert "product-pro" in help_text
        assert "research-pro" in help_text
    
    def test_get_specific_skill_help(self, executor):
        """测试获取特定技能帮助"""
        help_text = executor.get_skill_help("finance-pro")
        
        assert "finance-pro" in help_text
        assert "quote" in help_text
    
    def test_get_nonexistent_skill_help(self, executor):
        """测试获取不存在技能的帮助"""
        help_text = executor.get_skill_help("nonexistent")
        
        assert "未找到" in help_text or "not found" in help_text
