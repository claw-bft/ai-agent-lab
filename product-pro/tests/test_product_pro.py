#!/usr/bin/env python3
"""
Product Pro 测试套件
验证竞品分析、PRD生成、PPT生成、市场研究功能
"""

import sys
import os
import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 文件名是 product-pro.py，需要特殊导入
import importlib.util
spec = importlib.util.spec_from_file_location("product_pro", str(Path(__file__).parent.parent / "product-pro.py"))
product_pro = importlib.util.module_from_spec(spec)
spec.loader.exec_module(product_pro)

# 导入类
CompetitorInfo = product_pro.CompetitorInfo
PRDSection = product_pro.PRDSection
CompetitorAnalyzer = product_pro.CompetitorAnalyzer
PRDGenerator = product_pro.PRDGenerator
PPTGenerator = product_pro.PPTGenerator
MarketResearcher = product_pro.MarketResearcher


class TestCompetitorInfo(unittest.TestCase):
    """测试竞品信息数据类"""

    def test_competitor_info_creation(self):
        """测试创建竞品信息"""
        info = CompetitorInfo(
            name="TestProduct",
            positioning="Test positioning",
            strengths=["strength1", "strength2"],
            weaknesses=["weakness1"],
            target_users="Developers",
            pricing="$10/month"
        )
        self.assertEqual(info.name, "TestProduct")
        self.assertEqual(len(info.strengths), 2)
        self.assertEqual(info.key_features, [])  # 默认值

    def test_competitor_info_with_features(self):
        """测试带特性的竞品信息"""
        info = CompetitorInfo(
            name="TestProduct",
            positioning="Test",
            strengths=[],
            weaknesses=[],
            target_users="Users",
            pricing="Free",
            key_features=["feature1", "feature2"]
        )
        self.assertEqual(len(info.key_features), 2)


class TestCompetitorAnalyzer(unittest.TestCase):
    """测试竞品分析引擎"""

    def setUp(self):
        self.analyzer = CompetitorAnalyzer()

    def test_analyze_returns_dict(self):
        """测试分析返回字典"""
        result = self.analyzer.analyze("AI代码助手")
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("product", result)
        self.assertIn("competitors", result)

    def test_analyze_with_competitors(self):
        """测试指定竞品分析"""
        competitors = ["ProductA", "ProductB"]
        result = self.analyzer.analyze("MyProduct", competitors)
        self.assertEqual(len(result["competitors"]), 2)

    def test_infer_competitors_for_ai_code(self):
        """测试AI代码产品竞品推断"""
        comps = self.analyzer._infer_competitors("AI代码助手")
        self.assertIn("GitHub Copilot", comps)
        self.assertIn("Cursor", comps)

    def test_infer_competitors_for_notes(self):
        """测试笔记产品竞品推断"""
        comps = self.analyzer._infer_competitors("智能笔记应用")
        self.assertIn("Notion", comps)
        self.assertIn("Obsidian", comps)

    def test_infer_competitors_for_project_management(self):
        """测试项目管理产品竞品推断"""
        comps = self.analyzer._infer_competitors("项目管理工具")
        self.assertIn("Jira", comps)
        self.assertIn("Trello", comps)

    def test_infer_competitors_default(self):
        """测试默认竞品推断"""
        comps = self.analyzer._infer_competitors("未知产品XYZ")
        self.assertEqual(len(comps), 3)
        self.assertIn("市场领导者A", comps)

    def test_generate_market_overview(self):
        """测试市场概览生成"""
        overview = self.analyzer._generate_market_overview("TestProduct")
        self.assertIn("market_size", overview)
        self.assertIn("growth_rate", overview)
        self.assertIn("key_trends", overview)
        self.assertIsInstance(overview["key_trends"], list)

    def test_generate_comparison_matrix(self):
        """测试对比矩阵生成"""
        competitors = [
            {"name": "CompA"},
            {"name": "CompB"}
        ]
        matrix = self.analyzer._generate_comparison_matrix("MyProduct", competitors)
        self.assertIn("dimensions", matrix)
        self.assertIn("products", matrix)
        self.assertEqual(len(matrix["products"]), 3)  # MyProduct + 2 competitors

    def test_generate_insights(self):
        """测试洞察生成"""
        competitors = [{"name": "CompA"}, {"name": "CompB"}]
        insights = self.analyzer._generate_insights(competitors)
        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)


class TestPRDGenerator(unittest.TestCase):
    """测试PRD生成器"""

    def setUp(self):
        self.generator = PRDGenerator()

    def test_generate_returns_dict(self):
        """测试生成返回字典"""
        result = self.generator.generate("测试功能")
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("feature", result)
        self.assertIn("sections", result)

    def test_generate_prd_structure(self):
        """测试PRD结构完整"""
        result = self.generator.generate("AI助手")
        sections = result.get("sections", [])
        section_titles = [s["title"] for s in sections]

        # 验证关键章节存在
        self.assertIn("2. 背景与目标", section_titles)
        self.assertIn("3. 功能需求", section_titles)

    def test_standard_template(self):
        """测试标准模板"""
        sections = self.generator._standard_template("测试功能", {})
        self.assertIsInstance(sections, list)
        self.assertGreater(len(sections), 5)

        # 验证章节类型
        for section in sections:
            self.assertIsInstance(section, PRDSection)

    def test_lean_template(self):
        """测试精简模板"""
        sections = self.generator._lean_template("测试功能", {})
        self.assertIsInstance(sections, list)
        self.assertLess(len(sections), 6)  # 精简模板章节较少

    def test_detailed_template(self):
        """测试详细模板"""
        sections = self.generator._detailed_template("测试功能", {})
        self.assertIsInstance(sections, list)
        self.assertGreater(len(sections), 5)  # 详细模板章节较多

    def test_invalid_template(self):
        """测试无效模板"""
        result = self.generator.generate("测试功能", template="invalid")
        self.assertFalse(result["success"])
        self.assertIn("error", result)

    def test_to_markdown(self):
        """测试Markdown转换"""
        sections = [
            PRDSection(title="章节1", content="内容1"),
            PRDSection(title="章节2", content="内容2")
        ]
        md = self.generator._to_markdown("测试文档", sections)
        self.assertIn("# 测试文档", md)
        self.assertIn("内容1", md)
        self.assertIn("内容2", md)


class TestPPTGenerator(unittest.TestCase):
    """测试PPT生成器"""

    def setUp(self):
        self.generator = PPTGenerator()

    def test_generate_without_pptx(self):
        """测试无python-pptx时的处理"""
        # 模拟PPTX不可用
        with patch.object(product_pro, 'PPTX_AVAILABLE', False):
            generator = PPTGenerator()
            result = generator.generate("测试主题")
            self.assertFalse(result["success"])
            self.assertIn("error", result)

    def test_generate_default_outline(self):
        """测试默认大纲生成"""
        outline = self.generator._generate_default_outline("测试主题", 5)
        self.assertIsInstance(outline, list)
        self.assertEqual(len(outline), 5)

        # 验证大纲结构
        for item in outline:
            self.assertIn("type", item)
            self.assertIn("title", item)

    def test_outline_title_first_slide(self):
        """测试大纲第一个幻灯片是标题页"""
        outline = self.generator._generate_default_outline("测试主题", 5)
        self.assertEqual(outline[0]["type"], "title")
        self.assertEqual(outline[0]["title"], "测试主题")


class TestMarketResearcher(unittest.TestCase):
    """测试市场研究器"""

    def setUp(self):
        self.researcher = MarketResearcher()

    def test_conduct_research_returns_dict(self):
        """测试研究返回字典"""
        result = self.researcher.conduct_research("AI市场")
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("topic", result)

    def test_secondary_research(self):
        """测试二手研究"""
        result = self.researcher._secondary_research("AI市场", "企业用户", 0)
        self.assertIn("findings", result)
        self.assertIn("key_players", result["findings"])
        self.assertIsInstance(result["findings"]["key_players"], list)

    def test_competitive_research(self):
        """测试竞品研究"""
        result = self.researcher._competitive_research("AI产品", "企业用户", 0)
        self.assertIn("success", result)
        self.assertIn("competitors", result)


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def test_competitor_to_prd_flow(self):
        """测试竞品分析到PRD的流程"""
        # 竞品分析
        analyzer = CompetitorAnalyzer()
        comp_result = analyzer.analyze("AI编辑器", ["Cursor", "GitHub Copilot"])
        self.assertIn("insights", comp_result)

        # 生成PRD
        generator = PRDGenerator()
        prd_result = generator.generate("AI编辑器")
        self.assertIn("sections", prd_result)

    def test_end_to_end_product_planning(self):
        """测试端到端产品规划流程"""
        product_name = "智能客服系统"

        # 1. 竞品分析
        analyzer = CompetitorAnalyzer()
        competitors = analyzer.analyze(product_name, ["Zendesk", "Intercom"])
        self.assertTrue(competitors.get("success"))

        # 2. PRD生成
        generator = PRDGenerator()
        prd = generator.generate(product_name)
        self.assertTrue(prd.get("success"))

        # 3. 市场研究
        researcher = MarketResearcher()
        research = researcher.conduct_research(product_name)
        self.assertTrue(research.get("success"))

        # 验证所有结果可以序列化
        full_plan = {
            "competitors": competitors,
            "prd": prd,
            "research": research
        }
        json_str = json.dumps(full_plan, ensure_ascii=False, default=str)
        self.assertIsInstance(json_str, str)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestCompetitorInfo))
    suite.addTests(loader.loadTestsFromTestCase(TestCompetitorAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestPRDGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestPPTGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestMarketResearcher))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
