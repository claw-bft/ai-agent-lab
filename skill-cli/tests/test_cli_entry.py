#!/usr/bin/env python3
"""
Integration tests for skill-cli.py entry point
Tests CLI argument parsing, command execution, and output formatting
"""

import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the module under test - skill-cli.py uses hyphen, import as module
import importlib.util
spec = importlib.util.spec_from_file_location("skill_cli", 
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "skill-cli.py"))
skill_cli = importlib.util.module_from_spec(spec)
sys.modules["skill_cli"] = skill_cli

# Import executor first to satisfy dependency
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from executor import SkillExecutor

spec.loader.exec_module(skill_cli)

from skill_cli import (
    get_available_skills,
    parse_skill_md,
    execute_skill_command,
    build_command_map,
    handle_help,
    handle_info,
    handle_examples,
    handle_coding_generate,
    handle_coding_review,
    handle_coding_repo,
    handle_coding_cicd,
    handle_finance_quote,
    handle_finance_analyze,
    handle_finance_financial,
    handle_finance_alert,
    handle_product_competitor,
    handle_product_prd,
    handle_product_ppt,
    handle_product_research,
    handle_research_deep,
    handle_research_analyze,
    handle_research_search,
    handle_research_monitor,
    execute_natural_language,
    main,
    SKILLS_DIR
)


class TestGetAvailableSkills(unittest.TestCase):
    """Test get_available_skills function"""
    
    @patch('skill_cli.Path')
    def test_get_skills_empty_dir(self, mock_path):
        """Test when skills directory doesn't exist"""
        mock_instance = MagicMock()
        mock_instance.exists.return_value = False
        mock_path.return_value = mock_instance
        
        result = get_available_skills()
        self.assertEqual(result, [])
    
    @patch('skill_cli.Path')
    def test_get_skills_with_content(self, mock_path):
        """Test getting skills from directory"""
        mock_instance = MagicMock()
        mock_instance.exists.return_value = True
        
        # Mock directory entries
        mock_skill1 = MagicMock()
        mock_skill1.is_dir.return_value = True
        mock_skill1.name = 'skill1'
        mock_skill1.__truediv__ = MagicMock(return_value=MagicMock(exists=lambda: True))
        
        mock_skill2 = MagicMock()
        mock_skill2.is_dir.return_value = True
        mock_skill2.name = 'skill2'
        mock_skill2.__truediv__ = MagicMock(return_value=MagicMock(exists=lambda: True))
        
        mock_instance.iterdir.return_value = [mock_skill1, mock_skill2]
        mock_path.return_value = mock_instance
        
        result = get_available_skills()
        self.assertIn('skill1', result)
        self.assertIn('skill2', result)


class TestParseSkillMd(unittest.TestCase):
    """Test parse_skill_md function"""
    
    @patch('skill_cli.Path')
    def test_parse_nonexistent_skill(self, mock_path):
        """Test parsing a skill that doesn't exist"""
        mock_instance = MagicMock()
        mock_instance.exists.return_value = False
        mock_path.return_value = mock_instance
        
        result = parse_skill_md('nonexistent')
        self.assertEqual(result, {})
    
    @patch('skill_cli.Path')
    def test_parse_valid_skill(self, mock_path):
        """Test parsing a valid skill.md"""
        mock_file = MagicMock()
        mock_file.exists.return_value = True
        mock_file.read_text.return_value = """
name: test-skill
description: A test skill

## 使用示例

```bash
# Run the skill
skill-cli test-skill run
```
"""
        mock_path.return_value.__truediv__ = MagicMock(return_value=mock_file)
        
        result = parse_skill_md('test-skill')
        self.assertEqual(result.get('name'), 'test-skill')
        self.assertEqual(result.get('description'), 'A test skill')


class TestExecuteSkillCommand(unittest.TestCase):
    """Test execute_skill_command function"""
    
    @patch('skill_cli.parse_skill_md')
    def test_execute_nonexistent_skill(self, mock_parse):
        """Test executing a non-existent skill"""
        mock_parse.return_value = {}
        
        result = execute_skill_command('nonexistent', [])
        self.assertFalse(result['success'])
        self.assertIn('不存在', result['error'])
    
    @patch('skill_cli.parse_skill_md')
    def test_execute_skill_no_args(self, mock_parse):
        """Test executing skill with no arguments"""
        mock_parse.return_value = {
            'name': 'test-skill',
            'description': 'Test description',
            'examples': ['example1', 'example2']
        }
        
        result = execute_skill_command('test-skill', [])
        self.assertTrue(result['success'])
        self.assertEqual(result['skill'], 'test-skill')
        self.assertIn('example1', result['examples'])


class TestBuildCommandMap(unittest.TestCase):
    """Test build_command_map function"""
    
    def test_build_coding_map(self):
        """Test building command map for coding-pro"""
        cmd_map = build_command_map('coding-pro')
        self.assertIn('help', cmd_map)
        self.assertIn('info', cmd_map)
        self.assertIn('generate', cmd_map)
        self.assertIn('review', cmd_map)
        self.assertIn('repo', cmd_map)
        self.assertIn('cicd', cmd_map)
    
    def test_build_finance_map(self):
        """Test building command map for finance-pro"""
        cmd_map = build_command_map('finance-pro')
        self.assertIn('quote', cmd_map)
        self.assertIn('analyze', cmd_map)
        self.assertIn('financial', cmd_map)
        self.assertIn('alert', cmd_map)
    
    def test_build_product_map(self):
        """Test building command map for product-pro"""
        cmd_map = build_command_map('product-pro')
        self.assertIn('competitor', cmd_map)
        self.assertIn('prd', cmd_map)
        self.assertIn('ppt', cmd_map)
        self.assertIn('research', cmd_map)
    
    def test_build_research_map(self):
        """Test building command map for research-pro"""
        cmd_map = build_command_map('research-pro')
        self.assertIn('deep', cmd_map)
        self.assertIn('analyze', cmd_map)
        self.assertIn('search', cmd_map)
        self.assertIn('monitor', cmd_map)


class TestGenericHandlers(unittest.TestCase):
    """Test generic command handlers"""
    
    @patch('skill_cli.parse_skill_md')
    def test_handle_help(self, mock_parse):
        """Test help handler"""
        mock_parse.return_value = {
            'description': 'Test skill',
            'examples': ['ex1', 'ex2']
        }
        
        result = handle_help('test-skill', [])
        self.assertTrue(result['success'])
        self.assertEqual(result['skill'], 'test-skill')
        self.assertIn('ex1', result['examples'])
    
    @patch('skill_cli.Path')
    def test_handle_info(self, mock_path):
        """Test info handler"""
        mock_file = MagicMock()
        mock_file.exists.return_value = True
        mock_file.read_text.return_value = "test content"
        
        mock_skill_path = MagicMock()
        mock_skill_path.exists.return_value = True
        mock_skill_path.__truediv__ = MagicMock(return_value=mock_file)
        mock_path.return_value = mock_skill_path
        
        result = handle_info('test-skill', [])
        self.assertTrue(result['success'])
        self.assertEqual(result['skill'], 'test-skill')
        self.assertTrue(result['exists'])
    
    @patch('skill_cli.parse_skill_md')
    def test_handle_examples(self, mock_parse):
        """Test examples handler"""
        mock_parse.return_value = {
            'examples': ['example1', 'example2']
        }
        
        result = handle_examples('test-skill', [])
        self.assertTrue(result['success'])
        self.assertEqual(len(result['examples']), 2)


class TestCodingHandlers(unittest.TestCase):
    """Test coding-pro command handlers"""
    
    def test_handle_coding_generate(self):
        """Test code generation handler"""
        result = handle_coding_generate('coding-pro', ['--prompt', 'Create a function'])
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'code_generate')
        self.assertEqual(result['prompt'], 'Create a function')
    
    def test_handle_coding_generate_missing_prompt(self):
        """Test code generation with missing prompt"""
        result = handle_coding_generate('coding-pro', [])
        self.assertFalse(result['success'])
    
    def test_handle_coding_review(self):
        """Test code review handler"""
        result = handle_coding_review('coding-pro', ['--path', './src'])
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'code_review')
        self.assertEqual(result['path'], './src')
    
    def test_handle_coding_repo_create(self):
        """Test repo create subcommand"""
        result = handle_coding_repo('coding-pro', ['create'])
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'repo_create')
    
    def test_handle_coding_repo_no_subcommand(self):
        """Test repo with no subcommand"""
        result = handle_coding_repo('coding-pro', [])
        self.assertFalse(result['success'])
    
    def test_handle_coding_cicd(self):
        """Test CI/CD handler"""
        result = handle_coding_cicd('coding-pro', [])
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'cicd_setup')


class TestFinanceHandlers(unittest.TestCase):
    """Test finance-pro command handlers"""
    
    def test_handle_finance_quote(self):
        """Test stock quote handler"""
        result = handle_finance_quote('finance-pro', ['--symbol', '600519.SH'])
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'stock_quote')
        self.assertEqual(result['symbol'], '600519.SH')
    
    def test_handle_finance_quote_missing_symbol(self):
        """Test quote with missing symbol"""
        result = handle_finance_quote('finance-pro', [])
        self.assertFalse(result['success'])
    
    def test_handle_finance_analyze(self):
        """Test technical analysis handler"""
        result = handle_finance_analyze('finance-pro', ['--symbol', '000001.SZ'])
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'technical_analysis')
        self.assertIn('MACD', result['indicators'])
    
    def test_handle_finance_financial(self):
        """Test financial analysis handler"""
        result = handle_finance_financial('finance-pro', ['--symbol', 'AAPL'])
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'financial_analysis')
    
    def test_handle_finance_alert(self):
        """Test price alert handler"""
        result = handle_finance_alert('finance-pro', [
            '--symbol', 'TSLA',
            '--condition', 'price > 200'
        ])
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'price_alert')


class TestProductHandlers(unittest.TestCase):
    """Test product-pro command handlers"""
    
    def test_handle_product_competitor(self):
        """Test competitor analysis handler"""
        result = handle_product_competitor('product-pro', ['--product', 'AI助手'])
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'competitor_analysis')
        self.assertEqual(result['product'], 'AI助手')
    
    def test_handle_product_prd(self):
        """Test PRD creation handler"""
        result = handle_product_prd('product-pro', ['--feature', '登录功能'])
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'prd_create')
        self.assertEqual(result['template'], 'standard')
    
    def test_handle_product_ppt(self):
        """Test PPT generation handler"""
        result = handle_product_ppt('product-pro', ['--topic', '产品规划'])
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'ppt_create')
        self.assertEqual(result['slides'], 10)
    
    def test_handle_product_research(self):
        """Test user research handler"""
        result = handle_product_research('product-pro', [])
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'user_research')


class TestResearchHandlers(unittest.TestCase):
    """Test research-pro command handlers"""
    
    def test_handle_research_deep(self):
        """Test deep research handler"""
        result = handle_research_deep('research-pro', ['--topic', 'AI趋势'])
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'deep_research')
        self.assertEqual(result['depth'], 'comprehensive')
    
    def test_handle_research_analyze(self):
        """Test data analysis handler"""
        result = handle_research_analyze('research-pro', [
            '--file', 'data.csv',
            '--query', 'analyze trends'
        ])
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'data_analysis')
    
    def test_handle_research_search(self):
        """Test search handler"""
        result = handle_research_search('research-pro', ['--query', 'latest AI news'])
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'realtime_search')
    
    def test_handle_research_monitor(self):
        """Test competitor monitor handler"""
        result = handle_research_monitor('research-pro', ['--competitors', 'CompanyA,CompanyB'])
        self.assertTrue(result['success'])
        self.assertEqual(result['action'], 'competitor_monitor')
        self.assertEqual(len(result['competitors']), 2)


class TestNaturalLanguageExecution(unittest.TestCase):
    """Test natural language execution"""
    
    @patch('skill_cli.SkillExecutor')
    def test_execute_natural_language(self, mock_executor_class):
        """Test natural language execution with executor"""
        mock_executor = MagicMock()
        mock_result = MagicMock()
        mock_result.status.value = 'success'
        mock_result.skill_name = 'finance-pro'
        mock_result.command = '查询茅台股价'
        mock_result.output = {'price': 1800}
        mock_result.error = None
        mock_result.duration_ms = 100
        mock_result.metadata = {}
        mock_executor.execute_natural_language.return_value = mock_result
        mock_executor_class.return_value = mock_executor
        
        result = execute_natural_language('finance-pro', '查询茅台股价')
        self.assertTrue(result['success'])
        self.assertEqual(result['skill'], 'finance-pro')
    
    def test_execute_natural_language_fallback(self):
        """Test natural language fallback when executor fails"""
        with patch.dict('sys.modules', {'executor': None}):
            result = execute_natural_language('finance-pro', '查询茅台股价')
            self.assertTrue(result['success'])
            self.assertEqual(result['action'], 'natural_language')


class TestMainEntryPoint(unittest.TestCase):
    """Test main() entry point"""
    
    @patch('sys.argv', ['skill-cli'])
    @patch('skill_cli.get_available_skills')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_list_skills(self, mock_stdout, mock_get_skills):
        """Test main with no args (list skills)"""
        mock_get_skills.return_value = ['skill1', 'skill2']
        
        main()
        output = mock_stdout.getvalue()
        self.assertIn('skill1', output)
        self.assertIn('skill2', output)
    
    @patch('sys.argv', ['skill-cli', '--list'])
    @patch('skill_cli.get_available_skills')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_list_flag(self, mock_stdout, mock_get_skills):
        """Test main with --list flag"""
        mock_get_skills.return_value = ['skill1']
        
        main()
        output = mock_stdout.getvalue()
        self.assertIn('skill1', output)
    
    @patch('sys.argv', ['skill-cli', '-l'])
    @patch('skill_cli.get_available_skills')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_list_short_flag(self, mock_stdout, mock_get_skills):
        """Test main with -l flag"""
        mock_get_skills.return_value = ['skill1']
        
        main()
        output = mock_stdout.getvalue()
        self.assertIn('skill1', output)
    
    @patch('sys.argv', ['skill-cli', 'list', '--json'])
    @patch('skill_cli.get_available_skills')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_list_json_output(self, mock_stdout, mock_get_skills):
        """Test main with JSON output"""
        mock_get_skills.return_value = ['skill1', 'skill2']
        
        main()
        output = mock_stdout.getvalue()
        result = json.loads(output)
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 2)
    
    @patch('sys.argv', ['skill-cli', 'coding-pro', 'help'])
    @patch('skill_cli.execute_skill_command')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_execute_skill(self, mock_stdout, mock_execute):
        """Test main executing a skill command"""
        mock_execute.return_value = {
            'success': True,
            'message': 'Help displayed'
        }
        
        main()
        output = mock_stdout.getvalue()
        self.assertIn('✓', output)
    
    @patch('sys.argv', ['skill-cli', 'coding-pro', 'generate', '--prompt', 'test', '--json'])
    @patch('skill_cli.execute_skill_command')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_execute_skill_json(self, mock_stdout, mock_execute):
        """Test main with JSON output for skill command"""
        mock_execute.return_value = {
            'success': True,
            'action': 'code_generate'
        }
        
        main()
        output = mock_stdout.getvalue()
        result = json.loads(output)
        self.assertTrue(result['success'])
    
    @patch('sys.argv', ['skill-cli', 'coding-pro', 'invalid'])
    @patch('skill_cli.execute_skill_command')
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_execute_skill_error(self, mock_stdout, mock_execute):
        """Test main with skill execution error"""
        mock_execute.return_value = {
            'success': False,
            'error': 'Invalid command'
        }
        
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 1)


def run_tests():
    """Run all tests and return results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        TestGetAvailableSkills,
        TestParseSkillMd,
        TestExecuteSkillCommand,
        TestBuildCommandMap,
        TestGenericHandlers,
        TestCodingHandlers,
        TestFinanceHandlers,
        TestProductHandlers,
        TestResearchHandlers,
        TestNaturalLanguageExecution,
        TestMainEntryPoint
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
