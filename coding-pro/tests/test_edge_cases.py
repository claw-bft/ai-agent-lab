#!/usr/bin/env python3
"""
coding-pro 边界情况与异常测试
测试代码生成、代码审查、CI/CD配置的边界条件和错误处理
"""

import sys
import os
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util
spec = importlib.util.spec_from_file_location("coding_pro", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "coding-pro.py"))
coding_pro = importlib.util.module_from_spec(spec)
spec.loader.exec_module(coding_pro)

generate_code = coding_pro.generate_code
generate_project_structure = coding_pro.generate_project_structure
generate_api_project = coding_pro.generate_api_project
generate_cli_project = coding_pro.generate_cli_project
generate_web_project = coding_pro.generate_web_project
generate_generic_project = coding_pro.generate_generic_project
review_code = coding_pro.review_code
check_security_issues = coding_pro.check_security_issues
check_performance_issues = coding_pro.check_performance_issues
check_style_issues = coding_pro.check_style_issues
setup_cicd = coding_pro.setup_cicd
setup_github_actions = coding_pro.setup_github_actions
setup_gitlab_ci = coding_pro.setup_gitlab_ci
main = coding_pro.main


class TestGenerateCodeEdgeCases(unittest.TestCase):
    """测试代码生成边界情况"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_empty_prompt(self):
        """测试空提示"""
        result = generate_code("", self.temp_dir)
        self.assertTrue(result["success"])
        self.assertEqual(result["prompt"], "")
    
    def test_very_long_prompt(self):
        """测试超长提示"""
        long_prompt = "A" * 10000
        result = generate_code(long_prompt, self.temp_dir)
        self.assertTrue(result["success"])
        self.assertEqual(result["prompt"], long_prompt)
    
    def test_special_characters_in_prompt(self):
        """测试特殊字符提示"""
        special_prompt = "<script>alert(1)</script>'\"\\n\\t"
        result = generate_code(special_prompt, self.temp_dir)
        self.assertTrue(result["success"])
    
    def test_unicode_prompt(self):
        """测试Unicode提示"""
        unicode_prompt = "日本語 中文 한국어 العربية 🎉🎊"
        result = generate_code(unicode_prompt, self.temp_dir)
        self.assertTrue(result["success"])
    
    def test_invalid_output_dir(self):
        """测试无效输出目录"""
        # 使用无效路径
        result = generate_code("test", "/invalid/path/that/cannot/be/created")
        # 应该失败或处理错误
    
    def test_unsupported_language(self):
        """测试不支持的编程语言"""
        result = generate_code("test", self.temp_dir, language="unknown_lang_xyz")
        self.assertTrue(result["success"])
        # 应该回退到通用生成


class TestProjectStructureEdgeCases(unittest.TestCase):
    """测试项目结构生成边界情况"""
    
    def test_empty_prompt_structure(self):
        """测试空提示的结构生成"""
        structure = generate_project_structure("", "python")
        self.assertIn("files", structure)
    
    def test_case_insensitive_keywords(self):
        """测试大小写不敏感的关键词匹配"""
        # API相关
        structure = generate_project_structure("Create API", "python")
        self.assertEqual(structure["name"], "API Service")
        
        # CLI相关
        structure = generate_project_structure("Build CLI Tool", "python")
        self.assertEqual(structure["name"], "CLI Tool")
        
        # Web相关
        structure = generate_project_structure("Make Web App", "python")
        self.assertEqual(structure["name"], "Web Application")
    
    def test_multiple_keywords(self):
        """测试多个关键词同时存在"""
        structure = generate_project_structure("API and CLI tool", "python")
        # 应该根据第一个匹配的关键词选择
        self.assertIn("name", structure)


class TestReviewCodeEdgeCases(unittest.TestCase):
    """测试代码审查边界情况"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_nonexistent_path(self):
        """测试不存在的路径"""
        result = review_code("/nonexistent/path", ["security"])
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_empty_directory(self):
        """测试空目录"""
        result = review_code(self.temp_dir, ["security", "performance", "style"])
        self.assertTrue(result["success"])
        self.assertEqual(result["files_reviewed"], 0)
        self.assertEqual(result["total_issues"], 0)
    
    def test_no_rules_specified(self):
        """测试未指定规则"""
        # 创建测试文件
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("print('hello')")
        
        result = review_code(self.temp_dir, [])
        self.assertTrue(result["success"])
        # 没有规则时应该不检查任何内容
    
    def test_single_rule(self):
        """测试单条规则"""
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("password = 'secret'")
        
        result = review_code(self.temp_dir, ["security"])
        self.assertTrue(result["success"])
        self.assertEqual(result["files_reviewed"], 1)
    
    def test_nested_directories(self):
        """测试嵌套目录"""
        nested = Path(self.temp_dir) / "level1" / "level2"
        nested.mkdir(parents=True)
        (nested / "test.py").write_text("x = 1")
        
        result = review_code(self.temp_dir, ["style"])
        self.assertTrue(result["success"])
        self.assertEqual(result["files_reviewed"], 1)


class TestSecurityCheckEdgeCases(unittest.TestCase):
    """测试安全检查边界情况"""
    
    def test_empty_content(self):
        """测试空内容"""
        issues = check_security_issues("")
        self.assertIsInstance(issues, list)
    
    def test_no_security_issues(self):
        """测试无安全问题"""
        content = "x = 1\ny = 2\nprint(x + y)"
        issues = check_security_issues(content)
        # 可能没有发现问题
    
    def test_multiple_security_issues(self):
        """测试多个安全问题"""
        content = """
password = 'secret123'
query = "SELECT * FROM users WHERE id = %s" % user_id
"""
        issues = check_security_issues(content)
        self.assertGreater(len(issues), 0)
    
    def test_case_insensitive_password_check(self):
        """测试密码检查大小写不敏感"""
        content = "PASSWORD = 'secret'\nPassword = 'secret'"
        issues = check_security_issues(content)
        self.assertGreater(len(issues), 0)


class TestPerformanceCheckEdgeCases(unittest.TestCase):
    """测试性能检查边界情况"""
    
    def test_empty_content(self):
        """测试空内容"""
        issues = check_performance_issues("")
        self.assertIsInstance(issues, list)
    
    def test_loop_with_query(self):
        """测试循环中的查询"""
        content = """
for user in users:
    result = db.query(user.id)
"""
        issues = check_performance_issues(content)
        self.assertGreater(len(issues), 0)
    
    def test_no_performance_issues(self):
        """测试无性能问题"""
        content = "x = [1, 2, 3]\nfor i in x:\n    print(i)"
        issues = check_performance_issues(content)
        # 应该没有性能问题


class TestStyleCheckEdgeCases(unittest.TestCase):
    """测试风格检查边界情况"""
    
    def test_empty_content(self):
        """测试空内容"""
        issues = check_style_issues("")
        self.assertIsInstance(issues, list)
    
    def test_long_lines(self):
        """测试超长行"""
        content = "x = '" + "a" * 150 + "'"
        issues = check_style_issues(content)
        self.assertGreater(len(issues), 0)
    
    def test_multiple_long_lines(self):
        """测试多行超长"""
        content = "\n".join(["x = '" + "a" * 150 + "'" for _ in range(5)])
        issues = check_style_issues(content)
        self.assertEqual(len(issues), 5)
    
    def test_exactly_100_chars(self):
        """测试正好100字符"""
        content = "x = '" + "a" * 95 + "'"  # 正好100字符
        issues = check_style_issues(content)
        # 不应该报告问题


class TestCICDEdgeCases(unittest.TestCase):
    """测试CI/CD配置边界情况"""
    
    def setUp(self):
        self.original_dir = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        os.chdir(self.original_dir)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_unsupported_provider(self):
        """测试不支持的提供商"""
        result = setup_cicd("python", "unknown-provider")
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_unsupported_template(self):
        """测试不支持的模板"""
        result = setup_cicd("unknown-lang", "github-actions")
        # 应该使用默认模板
        self.assertTrue(result["success"])
    
    def test_github_actions_all_templates(self):
        """测试所有GitHub Actions模板"""
        templates = ["python", "node", "go", "rust"]
        for template in templates:
            result = setup_github_actions(template)
            self.assertTrue(result["success"])
            self.assertIn("workflow_file", result)
    
    def test_gitlab_ci_all_templates(self):
        """测试所有GitLab CI模板"""
        templates = ["python", "node"]
        for template in templates:
            result = setup_gitlab_ci(template)
            self.assertTrue(result["success"])
            self.assertIn("ci_file", result)
    
    def test_workflow_directory_creation(self):
        """测试工作流目录创建"""
        result = setup_github_actions("python")
        self.assertTrue(Path(".github/workflows/ci.yml").exists())


class TestMainFunctionEdgeCases(unittest.TestCase):
    """测试主函数边界情况"""
    
    @patch('sys.argv', ['coding-pro', 'generate'])
    def test_generate_without_prompt(self):
        """测试生成命令缺少提示"""
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 1)
    
    @patch('sys.argv', ['coding-pro', 'review'])
    def test_review_without_path(self):
        """测试审查命令缺少路径"""
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 1)
    
    @patch('sys.argv', ['coding-pro', 'unknown-command'])
    def test_unknown_command(self):
        """测试未知命令"""
        with self.assertRaises(SystemExit):
            main()


class TestGeneratedProjectContent(unittest.TestCase):
    """测试生成的项目内容"""
    
    def test_api_project_files(self):
        """测试API项目文件"""
        structure = generate_api_project("Test API", "python")
        self.assertIn("files", structure)
        file_paths = [f["path"] for f in structure["files"]]
        self.assertIn("main.py", file_paths)
        self.assertIn("requirements.txt", file_paths)
    
    def test_cli_project_files(self):
        """测试CLI项目文件"""
        structure = generate_cli_project("Test CLI", "python")
        self.assertIn("files", structure)
        file_paths = [f["path"] for f in structure["files"]]
        self.assertIn("cli.py", file_paths)
    
    def test_web_project_files(self):
        """测试Web项目文件"""
        structure = generate_web_project("Test Web", "javascript")
        self.assertIn("files", structure)
        file_paths = [f["path"] for f in structure["files"]]
        self.assertIn("index.html", file_paths)
    
    def test_generic_project_files(self):
        """测试通用项目文件"""
        structure = generate_generic_project("Test", "python")
        self.assertIn("files", structure)
        file_paths = [f["path"] for f in structure["files"]]
        self.assertIn("main.py", file_paths)


class TestResultFormat(unittest.TestCase):
    """测试结果格式"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generate_result_structure(self):
        """测试生成结果结构"""
        result = generate_code("test", self.temp_dir)
        self.assertIn("success", result)
        self.assertIn("prompt", result)
        self.assertIn("language", result)
        self.assertIn("output_dir", result)
        self.assertIn("files_created", result)
    
    def test_review_result_structure(self):
        """测试审查结果结构"""
        result = review_code(self.temp_dir, ["security"])
        self.assertIn("success", result)
        if result["success"]:
            self.assertIn("files_reviewed", result)
            self.assertIn("total_issues", result)
            self.assertIn("findings", result)
    
    def test_cicd_result_structure(self):
        """测试CI/CD结果结构"""
        result = setup_cicd("python", "github-actions")
        self.assertIn("success", result)
        if result["success"]:
            self.assertIn("provider", result)
            self.assertIn("template", result)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestGenerateCodeEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestProjectStructureEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestReviewCodeEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityCheckEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceCheckEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestStyleCheckEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestCICDEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestMainFunctionEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestGeneratedProjectContent))
    suite.addTests(loader.loadTestsFromTestCase(TestResultFormat))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
