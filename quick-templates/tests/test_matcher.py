#!/usr/bin/env python3
"""
Quick Templates 测试套件
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from matcher import match_template, get_help_text, TEMPLATES


class TestMatchTemplate(unittest.TestCase):
    """测试模板匹配功能"""
    
    def test_match_morning_report(self):
        """测试匹配早报模板"""
        result = match_template("早报")
        self.assertIsNotNone(result)
        self.assertEqual(result['template_id'], 'morning_report')
        
        result = match_template("生成morning report")
        self.assertEqual(result['template_id'], 'morning_report')
    
    def test_match_stock_analysis(self):
        """测试匹配股票分析模板"""
        result = match_template("分析股票 000001")
        self.assertIsNotNone(result)
        self.assertEqual(result['template_id'], 'stock_analysis')
        self.assertEqual(result['params'].get('symbol'), '000001')
    
    def test_match_deploy(self):
        """测试匹配部署模板"""
        result = match_template("部署 /path/to/project")
        self.assertIsNotNone(result)
        self.assertEqual(result['template_id'], 'deploy')
        self.assertEqual(result['params'].get('path'), '/path/to/project')
    
    def test_match_search(self):
        """测试匹配搜索模板"""
        result = match_template("搜索 OpenClaw最新动态")
        self.assertIsNotNone(result)
        self.assertEqual(result['template_id'], 'search')
        # 参数会被转换为小写
        self.assertEqual(result['params'].get('query'), 'openclaw最新动态')
    
    def test_match_code_review(self):
        """测试匹配代码审查模板"""
        result = match_template("审查代码 /path/to/file.py")
        self.assertIsNotNone(result)
        self.assertEqual(result['template_id'], 'code_review')
        self.assertEqual(result['params'].get('file_path'), '/path/to/file.py')
    
    def test_match_status(self):
        """测试匹配状态模板"""
        result = match_template("查看任务状态")
        self.assertIsNotNone(result)
        self.assertEqual(result['template_id'], 'status')
    
    def test_match_help(self):
        """测试匹配帮助模板"""
        result = match_template("帮助")
        self.assertIsNotNone(result)
        self.assertEqual(result['template_id'], 'help')
        
        result = match_template("怎么用")
        self.assertEqual(result['template_id'], 'help')
    
    def test_no_match(self):
        """测试无匹配"""
        result = match_template("随机输入内容")
        self.assertIsNone(result)
    
    def test_case_insensitive(self):
        """测试大小写不敏感"""
        result1 = match_template("早报")
        result3 = match_template("MORNING REPORT")
        
        self.assertEqual(result1['template_id'], 'morning_report')
        self.assertEqual(result3['template_id'], 'morning_report')


class TestGetHelpText(unittest.TestCase):
    """测试帮助文本功能"""
    
    def test_help_text_structure(self):
        """测试帮助文本结构"""
        help_text = get_help_text()
        
        self.assertIn('快速任务模板', help_text)
        self.assertIn('早报', help_text)
        self.assertIn('分析股票', help_text)
        self.assertIn('部署', help_text)
    
    def test_help_text_contains_all_templates(self):
        """测试帮助文本包含所有模板"""
        help_text = get_help_text()
        
        for template_id, template in TEMPLATES.items():
            self.assertIn(template['description'], help_text)


class TestParameterExtraction(unittest.TestCase):
    """测试参数提取功能"""
    
    def test_extract_single_param(self):
        """测试提取单个参数"""
        result = match_template("分析股票 000001.SZ")
        # 参数会被转换为小写
        self.assertEqual(result['params']['symbol'], '000001.sz')
    
    def test_extract_path_param(self):
        """测试提取路径参数"""
        result = match_template("部署 /home/user/project")
        self.assertEqual(result['params']['path'], '/home/user/project')
    
    def test_extract_query_param(self):
        """测试提取查询参数"""
        result = match_template("搜索 Python最佳实践")
        # 参数会被转换为小写
        self.assertEqual(result['params']['query'], 'python最佳实践')
    
    def test_no_params(self):
        """测试无参数模板"""
        result = match_template("早报")
        self.assertEqual(result['params'], {})
        
        result = match_template("帮助")
        self.assertEqual(result['params'], {})
    
    def test_empty_after_keyword(self):
        """测试关键词后无内容"""
        result = match_template("分析股票 ")
        self.assertEqual(result['params'], {})  # 空参数


class TestTemplateDefinitions(unittest.TestCase):
    """测试模板定义"""
    
    def test_all_templates_have_required_fields(self):
        """测试所有模板都有必需字段"""
        for template_id, template in TEMPLATES.items():
            self.assertIn('keywords', template)
            self.assertIn('description', template)
            self.assertIn('handler', template)
            self.assertIn('params', template)
            
            self.assertIsInstance(template['keywords'], list)
            self.assertIsInstance(template['params'], list)
    
    def test_no_duplicate_keywords(self):
        """测试无重复关键词"""
        all_keywords = []
        for template in TEMPLATES.values():
            all_keywords.extend([k.lower() for k in template['keywords']])
        
        self.assertEqual(len(all_keywords), len(set(all_keywords)))
    
    def test_keywords_not_empty(self):
        """测试关键词不为空"""
        for template in TEMPLATES.values():
            self.assertGreater(len(template['keywords']), 0)


class TestEdgeCases(unittest.TestCase):
    """测试边界情况"""
    
    def test_empty_input(self):
        """测试空输入"""
        result = match_template("")
        self.assertIsNone(result)
    
    def test_whitespace_only(self):
        """测试仅空白字符"""
        result = match_template("   ")
        self.assertIsNone(result)
    
    def test_multiple_keywords_in_input(self):
        """测试输入包含多个关键词"""
        # 应该匹配第一个找到的关键词
        result = match_template("早报 分析股票")
        self.assertIsNotNone(result)
    
    def test_partial_match(self):
        """测试部分匹配"""
        # "早" 应该不匹配 "早报"
        result = match_template("早")
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
