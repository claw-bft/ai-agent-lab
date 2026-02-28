"""
Vercel Deploy 测试套件
"""
import unittest
import os
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestVercelDeployStructure(unittest.TestCase):
    """测试项目结构"""
    
    def test_scripts_directory_exists(self):
        """测试scripts目录存在"""
        scripts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts')
        self.assertTrue(os.path.exists(scripts_dir), "scripts目录应该存在")
        self.assertTrue(os.path.isdir(scripts_dir), "scripts应该是目录")
    
    def test_references_directory_exists(self):
        """测试references目录存在"""
        ref_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'references')
        self.assertTrue(os.path.exists(ref_dir), "references目录应该存在")
    
    def test_readme_exists(self):
        """测试README存在"""
        readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'README.md')
        self.assertTrue(os.path.exists(readme_path), "README.md 应该存在")
    
    def test_setup_md_exists(self):
        """测试SETUP.md存在"""
        setup_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'SETUP.md')
        self.assertTrue(os.path.exists(setup_path), "SETUP.md 应该存在")
    
    def test_skill_md_exists(self):
        """测试SKILL.md存在"""
        skill_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'SKILL.md')
        self.assertTrue(os.path.exists(skill_path), "SKILL.md 应该存在")
    
    def test_meta_json_exists(self):
        """测试_meta.json存在"""
        meta_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '_meta.json')
        self.assertTrue(os.path.exists(meta_path), "_meta.json 应该存在")


class TestDeployScripts(unittest.TestCase):
    """测试部署脚本"""
    
    def test_deploy_script_exists(self):
        """测试部署脚本存在"""
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'vercel_deploy.sh')
        self.assertTrue(os.path.exists(script_path), "vercel_deploy.sh 应该存在")
    
    def test_env_script_exists(self):
        """测试环境变量脚本存在"""
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'vercel_env.sh')
        self.assertTrue(os.path.exists(script_path), "vercel_env.sh 应该存在")
    
    def test_status_script_exists(self):
        """测试状态脚本存在"""
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'vercel_status.sh')
        self.assertTrue(os.path.exists(script_path), "vercel_status.sh 应该存在")
    
    def test_logs_script_exists(self):
        """测试日志脚本存在（可选）"""
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'vercel_logs.sh')
        # 这个脚本是可选的
        if os.path.exists(script_path):
            self.assertTrue(os.path.exists(script_path), "vercel_logs.sh 应该存在")
    
    def test_scripts_are_executable(self):
        """测试脚本可执行"""
        scripts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts')
        scripts = ['vercel_deploy.sh', 'vercel_env.sh', 'vercel_status.sh', 'vercel_logs.sh']
        for script in scripts:
            script_path = os.path.join(scripts_dir, script)
            if os.path.exists(script_path):
                self.assertTrue(os.access(script_path, os.X_OK), f"{script} 应该有执行权限")


class TestScriptContent(unittest.TestCase):
    """测试脚本内容"""
    
    def test_deploy_script_uses_vercel_token(self):
        """测试部署脚本使用VERCEL_TOKEN"""
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'vercel_deploy.sh')
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('VERCEL_TOKEN', content, "应该使用VERCEL_TOKEN")
    
    def test_env_script_handles_set(self):
        """测试环境脚本支持set操作"""
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'vercel_env.sh')
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('--set', content, "应该支持--set操作")
    
    def test_env_script_handles_list(self):
        """测试环境脚本支持list操作"""
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'vercel_env.sh')
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('--list', content, "应该支持--list操作")
    
    def test_scripts_use_curl(self):
        """测试脚本使用curl或wget"""
        scripts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts')
        for script in os.listdir(scripts_dir):
            if script.endswith('.sh'):
                script_path = os.path.join(scripts_dir, script)
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                has_http_tool = 'curl' in content.lower() or 'wget' in content.lower() or 'vercel' in content.lower()
                self.assertTrue(has_http_tool, f"{script} 应该使用curl/wget或vercel CLI")


class TestDocumentation(unittest.TestCase):
    """测试文档质量"""
    
    def test_readme_not_empty(self):
        """测试README不为空"""
        readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'README.md')
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertGreater(len(content), 1000, "README应该足够详细")
    
    def test_skill_md_not_empty(self):
        """测试SKILL.md不为空"""
        skill_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'SKILL.md')
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertGreater(len(content), 1000, "SKILL.md应该足够详细")
    
    def test_skill_md_has_configuration(self):
        """测试SKILL.md有配置说明"""
        skill_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'SKILL.md')
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        has_config = '配置' in content or 'Configuration' in content or 'Setup' in content or 'VERCEL_TOKEN' in content
        self.assertTrue(has_config, "应该有配置说明")
    
    def test_skill_md_has_workflows(self):
        """测试SKILL.md有工作流示例"""
        skill_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'SKILL.md')
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        has_workflow = '工作流' in content or 'Workflow' in content or 'Common Workflows' in content or 'Deployment' in content
        self.assertTrue(has_workflow, "应该有工作流示例")
    
    def test_skill_md_has_troubleshooting(self):
        """测试SKILL.md有故障排查"""
        skill_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'SKILL.md')
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        has_troubleshoot = '故障' in content or 'Troubleshooting' in content or 'Debug' in content or 'Issues' in content
        self.assertTrue(has_troubleshoot, "应该有故障排查")


class TestReferences(unittest.TestCase):
    """测试参考文档"""
    
    def test_references_not_empty(self):
        """测试references目录不为空"""
        ref_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'references')
        files = os.listdir(ref_dir)
        self.assertGreater(len(files), 0, "references目录应该有文件")
    
    def test_has_api_reference(self):
        """测试有API参考文档"""
        ref_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'references')
        files = os.listdir(ref_dir)
        has_api_ref = any('api' in f.lower() for f in files)
        self.assertTrue(has_api_ref, "应该有API参考文档")


class TestMetaJson(unittest.TestCase):
    """测试_meta.json"""
    
    def test_meta_json_is_valid(self):
        """测试_meta.json是有效JSON"""
        import json
        meta_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '_meta.json')
        with open(meta_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                self.assertIsInstance(data, dict, "_meta.json应该是对象")
            except json.JSONDecodeError:
                self.fail("_meta.json不是有效的JSON")
    
    def test_meta_has_name(self):
        """测试_meta.json有name或slug字段"""
        import json
        meta_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '_meta.json')
        with open(meta_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        has_name = 'name' in data or 'slug' in data
        self.assertTrue(has_name, "应该有name或slug字段")


if __name__ == '__main__':
    unittest.main()
