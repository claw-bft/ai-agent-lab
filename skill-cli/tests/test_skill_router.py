#!/usr/bin/env python3
"""
Test suite for skill-cli skill_router module
Comprehensive tests for the Skill Router functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from intent_parser import Intent, IntentType
from skill_router import SkillRoute, SkillRouter


class TestSkillRoute(unittest.TestCase):
    """Test SkillRoute dataclass"""

    def test_route_creation(self):
        """Test creating a SkillRoute"""
        route = SkillRoute(
            skill_name="finance-pro",
            command="quote",
            args=["--symbol", "600519.SH"],
            confidence=0.95,
            reason="Intent matched directly"
        )

        self.assertEqual(route.skill_name, "finance-pro")
        self.assertEqual(route.command, "quote")
        self.assertEqual(route.args, ["--symbol", "600519.SH"])
        self.assertEqual(route.confidence, 0.95)
        self.assertEqual(route.reason, "Intent matched directly")

    def test_route_with_empty_args(self):
        """Test SkillRoute with empty args"""
        route = SkillRoute(
            skill_name="coding-pro",
            command="help",
            args=[],
            confidence=0.5,
            reason="Default route"
        )

        self.assertEqual(route.args, [])


class TestSkillRouterInitialization(unittest.TestCase):
    """Test SkillRouter initialization"""

    def test_router_init(self):
        """Test router initializes correctly"""
        router = SkillRouter()
        self.assertIsInstance(router.skills_dir, Path)

    @patch.object(Path, 'exists')
    @patch.object(Path, 'iterdir')
    def test_discover_skills(self, mock_iterdir, mock_exists):
        """Test skill discovery"""
        mock_exists.return_value = True

        # Mock directory structure
        mock_dir1 = Mock()
        mock_dir1.name = "finance-pro"
        mock_dir1.is_dir.return_value = True
        mock_dir1.__truediv__ = Mock(return_value=Mock(exists=lambda: True))

        mock_dir2 = Mock()
        mock_dir2.name = "coding-pro"
        mock_dir2.is_dir.return_value = True
        mock_dir2.__truediv__ = Mock(return_value=Mock(exists=lambda: True))

        mock_iterdir.return_value = [mock_dir1, mock_dir2]

        router = SkillRouter()
        self.assertIn("finance-pro", router.available_skills)
        self.assertIn("coding-pro", router.available_skills)

    @patch.object(Path, 'exists')
    def test_discover_skills_no_dir(self, mock_exists):
        """Test skill discovery when directory doesn't exist"""
        mock_exists.return_value = False

        router = SkillRouter()
        self.assertEqual(router.available_skills, [])


class TestSkillRouterDirectMapping(unittest.TestCase):
    """Test direct intent to skill mapping"""

    def setUp(self):
        self.router = SkillRouter()

    def test_route_get_quote(self):
        """Test routing GET_QUOTE intent"""
        intent = Intent(
            type=IntentType.GET_QUOTE,
            confidence=0.9,
            entities={"symbol": "600519.SH"},
            raw_text="查询茅台股价"
        )

        route = self.router.route(intent)
        self.assertEqual(route.skill_name, "finance-pro")
        self.assertEqual(route.command, "quote")
        self.assertEqual(route.args, ["--symbol", "600519.SH"])
        self.assertGreater(route.confidence, 0.7)

    def test_route_analyze_stock(self):
        """Test routing ANALYZE_STOCK intent"""
        intent = Intent(
            type=IntentType.ANALYZE_STOCK,
            confidence=0.85,
            entities={"symbol": "000001.SZ"},
            raw_text="分析平安银行"
        )

        route = self.router.route(intent)
        self.assertEqual(route.skill_name, "finance-pro")
        self.assertEqual(route.command, "analyze")
        self.assertEqual(route.args, ["--symbol", "000001.SZ"])

    def test_route_set_alert(self):
        """Test routing SET_ALERT intent"""
        intent = Intent(
            type=IntentType.SET_ALERT,
            confidence=0.8,
            entities={"symbol": "600519.SH", "condition": ">1800"},
            raw_text="茅台超过1800提醒我"
        )

        route = self.router.route(intent)
        self.assertEqual(route.skill_name, "finance-pro")
        self.assertEqual(route.command, "alert")

    def test_route_generate_code(self):
        """Test routing GENERATE_CODE intent"""
        intent = Intent(
            type=IntentType.GENERATE_CODE,
            confidence=0.9,
            entities={"prompt": "Python爬虫", "language": "Python"},
            raw_text="用Python写个爬虫"
        )

        route = self.router.route(intent)
        self.assertEqual(route.skill_name, "coding-pro")
        self.assertEqual(route.command, "generate")
        self.assertIn("--prompt", route.args)
        self.assertIn("Python爬虫", route.args)

    def test_route_review_code(self):
        """Test routing REVIEW_CODE intent"""
        intent = Intent(
            type=IntentType.REVIEW_CODE,
            confidence=0.85,
            entities={"path": "main.py"},
            raw_text="审查main.py"
        )

        route = self.router.route(intent)
        self.assertEqual(route.skill_name, "coding-pro")
        self.assertEqual(route.command, "review")
        self.assertEqual(route.args, ["--path", "main.py"])

    def test_route_research(self):
        """Test routing RESEARCH intent"""
        intent = Intent(
            type=IntentType.RESEARCH,
            confidence=0.9,
            entities={"topic": "AI发展趋势"},
            raw_text="研究AI发展趋势"
        )

        route = self.router.route(intent)
        self.assertEqual(route.skill_name, "research-pro")
        self.assertEqual(route.command, "deep")
        self.assertEqual(route.args, ["--topic", "AI发展趋势"])

    def test_route_analyze_data(self):
        """Test routing ANALYZE_DATA intent"""
        intent = Intent(
            type=IntentType.ANALYZE_DATA,
            confidence=0.8,
            entities={"file": "data.csv", "query": "销售统计"},
            raw_text="分析data.csv中的销售统计"
        )

        route = self.router.route(intent)
        self.assertEqual(route.skill_name, "research-pro")
        self.assertEqual(route.command, "analyze")
        self.assertIn("--file", route.args)
        self.assertIn("data.csv", route.args)

    def test_route_create_prd(self):
        """Test routing CREATE_PRD intent"""
        intent = Intent(
            type=IntentType.CREATE_PRD,
            confidence=0.85,
            entities={"feature": "登录功能"},
            raw_text="为登录功能写PRD"
        )

        route = self.router.route(intent)
        self.assertEqual(route.skill_name, "product-pro")
        self.assertEqual(route.command, "prd")
        self.assertEqual(route.args, ["--feature", "登录功能"])

    def test_route_competitor_analysis(self):
        """Test routing COMPETITOR_ANALYSIS intent"""
        intent = Intent(
            type=IntentType.COMPETITOR_ANALYSIS,
            confidence=0.8,
            entities={"product": "AI助手"},
            raw_text="分析AI助手竞品"
        )

        route = self.router.route(intent)
        self.assertEqual(route.skill_name, "product-pro")
        self.assertEqual(route.command, "competitor")
        self.assertEqual(route.args, ["--product", "AI助手"])


class TestSkillRouterSkillHint(unittest.TestCase):
    """Test routing with skill hints"""

    def setUp(self):
        self.router = SkillRouter()

    def test_route_with_skill_hint(self):
        """Test routing when skill hint is provided"""
        intent = Intent(
            type=IntentType.UNKNOWN,
            confidence=0.5,
            entities={},
            raw_text="随便看看",
            skill_hint="finance-pro"
        )

        # Add finance-pro to available skills for this test
        self.router.available_skills = ["finance-pro", "coding-pro"]

        route = self.router.route(intent)
        self.assertEqual(route.skill_name, "finance-pro")
        self.assertEqual(route.command, "help")

    def test_route_with_unavailable_skill_hint(self):
        """Test routing when skill hint is not available"""
        intent = Intent(
            type=IntentType.UNKNOWN,
            confidence=0.5,
            entities={},
            raw_text="随便看看",
            skill_hint="unknown-pro"
        )

        self.router.available_skills = ["finance-pro", "coding-pro"]

        route = self.router.route(intent)
        # Should fall back to research-pro as default
        self.assertEqual(route.skill_name, "research-pro")


class TestSkillRouterSmartMatch(unittest.TestCase):
    """Test smart skill matching"""

    def setUp(self):
        self.router = SkillRouter()

    def test_smart_match_finance_aliases(self):
        """Test smart matching finance aliases"""
        intent = Intent(
            type=IntentType.UNKNOWN,
            confidence=0.4,
            entities={},
            raw_text="股票查询"
        )

        result = self.router._smart_match(intent)
        self.assertEqual(result, "finance-pro")

    def test_smart_match_coding_aliases(self):
        """Test smart matching coding aliases"""
        intent = Intent(
            type=IntentType.UNKNOWN,
            confidence=0.4,
            entities={},
            raw_text="帮我写代码"
        )

        result = self.router._smart_match(intent)
        self.assertEqual(result, "coding-pro")

    def test_smart_match_product_aliases(self):
        """Test smart matching product aliases"""
        intent = Intent(
            type=IntentType.UNKNOWN,
            confidence=0.4,
            entities={},
            raw_text="产品分析"
        )

        result = self.router._smart_match(intent)
        self.assertEqual(result, "product-pro")

    def test_smart_match_research_aliases(self):
        """Test smart matching research aliases"""
        intent = Intent(
            type=IntentType.UNKNOWN,
            confidence=0.4,
            entities={},
            raw_text="研究一下"
        )

        result = self.router._smart_match(intent)
        self.assertEqual(result, "research-pro")

    def test_smart_match_no_match(self):
        """Test smart matching with no match"""
        intent = Intent(
            type=IntentType.UNKNOWN,
            confidence=0.4,
            entities={},
            raw_text="随便说点什么"
        )

        result = self.router._smart_match(intent)
        self.assertIsNone(result)


class TestSkillRouterDefaultRoute(unittest.TestCase):
    """Test default routing behavior"""

    def setUp(self):
        self.router = SkillRouter()

    def test_default_route(self):
        """Test default route for unknown intent"""
        intent = Intent(
            type=IntentType.UNKNOWN,
            confidence=0.3,
            entities={},
            raw_text="随便看看"
        )

        route = self.router.route(intent)
        self.assertEqual(route.skill_name, "research-pro")
        self.assertEqual(route.command, "deep")
        self.assertEqual(route.args, ["--topic", "随便看看"])
        self.assertLess(route.confidence, 0.5)


class TestSkillRouterBuildArgs(unittest.TestCase):
    """Test argument building"""

    def setUp(self):
        self.router = SkillRouter()

    def test_build_args_finance_quote(self):
        """Test building args for finance quote"""
        intent = Intent(
            type=IntentType.GET_QUOTE,
            confidence=0.9,
            entities={"symbol": "600519.SH"},
            raw_text="查询茅台"
        )

        args = self.router._build_args(intent, "finance-pro", "quote")
        self.assertEqual(args, ["--symbol", "600519.SH"])

    def test_build_args_finance_analyze(self):
        """Test building args for finance analyze"""
        intent = Intent(
            type=IntentType.ANALYZE_STOCK,
            confidence=0.9,
            entities={"symbol": "000001.SZ", "indicators": "MA,RSI"},
            raw_text="分析平安银行技术指标"
        )

        args = self.router._build_args(intent, "finance-pro", "analyze")
        self.assertIn("--symbol", args)
        self.assertIn("000001.SZ", args)
        self.assertIn("--indicators", args)
        self.assertIn("MA,RSI", args)

    def test_build_args_coding_generate(self):
        """Test building args for coding generate"""
        intent = Intent(
            type=IntentType.GENERATE_CODE,
            confidence=0.9,
            entities={"prompt": "Python爬虫", "language": "Python"},
            raw_text="用Python写个爬虫"
        )

        args = self.router._build_args(intent, "coding-pro", "generate")
        self.assertIn("--prompt", args)
        self.assertIn("Python爬虫", args)
        self.assertIn("--language", args)
        self.assertIn("Python", args)

    def test_build_args_coding_review(self):
        """Test building args for coding review"""
        intent = Intent(
            type=IntentType.REVIEW_CODE,
            confidence=0.9,
            entities={"path": "./src"},
            raw_text="审查代码"
        )

        args = self.router._build_args(intent, "coding-pro", "review")
        self.assertEqual(args, ["--path", "./src"])

    def test_build_args_research_deep(self):
        """Test building args for research deep"""
        intent = Intent(
            type=IntentType.RESEARCH,
            confidence=0.9,
            entities={"topic": "AI发展趋势"},
            raw_text="研究AI"
        )

        args = self.router._build_args(intent, "research-pro", "deep")
        self.assertEqual(args, ["--topic", "AI发展趋势"])

    def test_build_args_research_analyze(self):
        """Test building args for research analyze"""
        intent = Intent(
            type=IntentType.ANALYZE_DATA,
            confidence=0.9,
            entities={"file": "data.csv", "query": "统计"},
            raw_text="分析数据"
        )

        args = self.router._build_args(intent, "research-pro", "analyze")
        self.assertIn("--file", args)
        self.assertIn("data.csv", args)
        self.assertIn("--query", args)
        self.assertIn("统计", args)

    def test_build_args_product_competitor(self):
        """Test building args for product competitor"""
        intent = Intent(
            type=IntentType.COMPETITOR_ANALYSIS,
            confidence=0.9,
            entities={"product": "AI助手"},
            raw_text="分析竞品"
        )

        args = self.router._build_args(intent, "product-pro", "competitor")
        self.assertEqual(args, ["--product", "AI助手"])

    def test_build_args_product_prd(self):
        """Test building args for product PRD"""
        intent = Intent(
            type=IntentType.CREATE_PRD,
            confidence=0.9,
            entities={"feature": "登录功能"},
            raw_text="写PRD"
        )

        args = self.router._build_args(intent, "product-pro", "prd")
        self.assertEqual(args, ["--feature", "登录功能"])

    def test_build_args_empty_entities(self):
        """Test building args with empty entities"""
        intent = Intent(
            type=IntentType.GET_QUOTE,
            confidence=0.9,
            entities={},
            raw_text="查询股票"
        )

        args = self.router._build_args(intent, "finance-pro", "quote")
        self.assertEqual(args, [])


class TestSkillRouterBuildArgsFromEntities(unittest.TestCase):
    """Test building args from entities"""

    def setUp(self):
        self.router = SkillRouter()

    def test_build_from_entities(self):
        """Test building args from entities dict"""
        entities = {
            "symbol": "600519.SH",
            "condition": ">1800"
        }

        args = self.router._build_args_from_entities(entities)
        self.assertIn("--symbol", args)
        self.assertIn("600519.SH", args)
        self.assertIn("--condition", args)
        self.assertIn(">1800", args)

    def test_build_from_empty_entities(self):
        """Test building args from empty entities"""
        args = self.router._build_args_from_entities({})
        self.assertEqual(args, [])

    def test_build_skips_none_values(self):
        """Test that None values are skipped"""
        entities = {
            "symbol": "600519.SH",
            "condition": None
        }

        args = self.router._build_args_from_entities(entities)
        self.assertIn("--symbol", args)
        self.assertNotIn("--condition", args)


class TestSkillRouterSkillInfo(unittest.TestCase):
    """Test skill info retrieval"""

    def setUp(self):
        self.router = SkillRouter()

    @patch.object(Path, 'exists')
    def test_get_skill_info_exists(self, mock_exists):
        """Test getting info for existing skill"""
        mock_exists.return_value = True

        with patch.object(Path, 'read_text', return_value="---\nname: test\n---\nContent"):
            info = self.router.get_skill_info("finance-pro")
            self.assertTrue(info["exists"])
            self.assertEqual(info["name"], "finance-pro")

    @patch.object(Path, 'exists')
    def test_get_skill_info_not_exists(self, mock_exists):
        """Test getting info for non-existing skill"""
        mock_exists.return_value = False

        info = self.router.get_skill_info("nonexistent")
        self.assertFalse(info["exists"])


class TestSkillRouterListAvailable(unittest.TestCase):
    """Test listing available skills"""

    def setUp(self):
        self.router = SkillRouter()

    def test_list_available_skills(self):
        """Test listing available skills"""
        self.router.available_skills = ["finance-pro", "coding-pro"]

        skills = self.router.list_available_skills()
        self.assertEqual(len(skills), 2)
        self.assertEqual(skills[0]["name"], "finance-pro")
        self.assertEqual(skills[1]["name"], "coding-pro")


class TestSkillRouterConfidence(unittest.TestCase):
    """Test confidence calculation in routing"""

    def setUp(self):
        self.router = SkillRouter()

    def test_direct_mapping_confidence(self):
        """Test confidence for direct mapping"""
        intent = Intent(
            type=IntentType.GET_QUOTE,
            confidence=1.0,
            entities={"symbol": "600519.SH"},
            raw_text="查询茅台"
        )

        route = self.router.route(intent)
        # Direct mapping should have confidence around 0.9
        self.assertGreaterEqual(route.confidence, 0.8)
        self.assertLessEqual(route.confidence, 1.0)

    def test_skill_hint_confidence(self):
        """Test confidence for skill hint routing"""
        intent = Intent(
            type=IntentType.UNKNOWN,
            confidence=0.5,
            entities={},
            raw_text="测试",
            skill_hint="finance-pro"
        )

        self.router.available_skills = ["finance-pro"]

        route = self.router.route(intent)
        # Skill hint should have lower confidence
        self.assertLess(route.confidence, 0.5)

    def test_smart_match_confidence(self):
        """Test confidence for smart match"""
        intent = Intent(
            type=IntentType.UNKNOWN,
            confidence=0.4,
            entities={},
            raw_text="股票查询"
        )

        route = self.router.route(intent)
        # Smart match should have confidence around 0.4
        self.assertLessEqual(route.confidence, 0.5)

    def test_default_route_confidence(self):
        """Test confidence for default route"""
        intent = Intent(
            type=IntentType.UNKNOWN,
            confidence=0.3,
            entities={},
            raw_text="随便说点什么"
        )

        route = self.router.route(intent)
        # Default route should have low confidence
        self.assertEqual(route.confidence, 0.3)


def run_tests():
    """Run all tests and return results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestSkillRoute,
        TestSkillRouterInitialization,
        TestSkillRouterDirectMapping,
        TestSkillRouterSkillHint,
        TestSkillRouterSmartMatch,
        TestSkillRouterDefaultRoute,
        TestSkillRouterBuildArgs,
        TestSkillRouterBuildArgsFromEntities,
        TestSkillRouterSkillInfo,
        TestSkillRouterListAvailable,
        TestSkillRouterConfidence,
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
