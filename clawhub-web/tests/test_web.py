"""
ClawHub Web 前端测试套件
"""
import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestClawHubWebStructure(unittest.TestCase):
    """测试项目结构"""
    
    def test_index_html_exists(self):
        """测试主页面存在"""
        index_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'index.html')
        self.assertTrue(os.path.exists(index_path), "index.html 应该存在")
    
    def test_styles_css_exists(self):
        """测试样式文件存在"""
        css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles.css')
        self.assertTrue(os.path.exists(css_path), "styles.css 应该存在")
    
    def test_app_js_exists(self):
        """测试JS文件存在"""
        js_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.js')
        self.assertTrue(os.path.exists(js_path), "app.js 应该存在")
    
    def test_readme_exists(self):
        """测试README存在"""
        readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'README.md')
        self.assertTrue(os.path.exists(readme_path), "README.md 应该存在")
    
    def test_skill_md_exists(self):
        """测试SKILL.md存在"""
        skill_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'SKILL.md')
        self.assertTrue(os.path.exists(skill_path), "SKILL.md 应该存在")


class TestIndexHtml(unittest.TestCase):
    """测试HTML内容"""
    
    def setUp(self):
        index_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            self.html_content = f.read()
    
    def test_html_has_title(self):
        """测试HTML有标题"""
        self.assertIn('<title>', self.html_content, "应该有title标签")
        self.assertIn('ClawHub', self.html_content, "标题应该包含ClawHub")
    
    def test_html_has_search(self):
        """测试有搜索功能"""
        self.assertIn('search', self.html_content.lower(), "应该有搜索功能")
    
    def test_html_has_skill_list(self):
        """测试有技能列表容器"""
        self.assertIn('skill', self.html_content.lower(), "应该有技能相关元素")
    
    def test_html_links_css(self):
        """测试引用了CSS"""
        self.assertIn('styles.css', self.html_content, "应该引用styles.css")
    
    def test_html_links_js(self):
        """测试引用了JS"""
        self.assertIn('app.js', self.html_content, "应该引用app.js")
    
    def test_html_is_valid_structure(self):
        """测试HTML结构完整"""
        self.assertIn('<!DOCTYPE html>', self.html_content, "应该有DOCTYPE声明")
        self.assertIn('<html', self.html_content, "应该有html标签")
        self.assertIn('<head>', self.html_content, "应该有head标签")
        self.assertIn('<body>', self.html_content, "应该有body标签")


class TestAppJs(unittest.TestCase):
    """测试JavaScript内容"""
    
    def setUp(self):
        js_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            self.js_content = f.read()
    
    def test_js_has_mock_data(self):
        """测试有数据加载功能"""
        self.assertIn('skillsData', self.js_content, "应该有skillsData")
    
    def test_js_has_render_function(self):
        """测试有渲染函数"""
        self.assertIn('render', self.js_content.lower(), "应该有渲染函数")
    
    def test_js_has_search_function(self):
        """测试有搜索功能"""
        self.assertIn('search', self.js_content.lower(), "应该有搜索功能")
    
    def test_js_has_filter_function(self):
        """测试有过滤功能"""
        self.assertIn('filter', self.js_content.lower(), "应该有过滤功能")
    
    def test_js_has_rating_function(self):
        """测试有评分功能"""
        self.assertIn('rating', self.js_content.lower(), "应该有评分功能")


class TestStylesCss(unittest.TestCase):
    """测试CSS内容"""
    
    def setUp(self):
        css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'styles.css')
        with open(css_path, 'r', encoding='utf-8') as f:
            self.css_content = f.read()
    
    def test_css_has_dark_mode(self):
        """测试有深色模式"""
        self.assertIn('dark', self.css_content.lower(), "应该有深色模式样式")
    
    def test_css_has_responsive(self):
        """测试有响应式设计"""
        self.assertIn('@media', self.css_content, "应该有媒体查询")
    
    def test_css_has_variables(self):
        """测试有CSS变量"""
        self.assertIn('--', self.css_content, "应该有CSS变量")
    
    def test_css_has_skill_card(self):
        """测试有技能卡片样式"""
        self.assertIn('skill', self.css_content.lower(), "应该有技能卡片样式")


class TestDocumentation(unittest.TestCase):
    """测试文档质量"""
    
    def test_readme_not_empty(self):
        """测试README不为空"""
        readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'README.md')
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertGreater(len(content), 500, "README应该足够详细")
    
    def test_skill_md_not_empty(self):
        """测试SKILL.md不为空"""
        skill_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'SKILL.md')
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertGreater(len(content), 500, "SKILL.md应该足够详细")
    
    def test_skill_md_has_usage(self):
        """测试SKILL.md有使用指南"""
        skill_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'SKILL.md')
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('使用', content, "应该有使用指南")
    
    def test_skill_md_has_features(self):
        """测试SKILL.md有功能特性"""
        skill_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'SKILL.md')
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('功能', content, "应该有功能特性")


class TestMockData(unittest.TestCase):
    """测试模拟数据"""
    
    def setUp(self):
        js_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            self.js_content = f.read()
    
    def test_mock_data_has_skills(self):
        """测试模拟数据包含技能"""
        self.assertIn('skills', self.js_content, "应该有skills数据")
    
    def test_mock_data_has_categories(self):
        """测试模拟数据包含分类"""
        self.assertIn('categor', self.js_content.lower(), "应该有分类数据")
    
    def test_mock_data_has_stats(self):
        """测试模拟数据包含统计"""
        self.assertIn('stat', self.js_content.lower(), "应该有统计数据")


if __name__ == '__main__':
    unittest.main()
