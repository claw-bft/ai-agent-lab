#!/usr/bin/env python3
"""
补充测试文件 - 提升 coding-pro 测试覆盖率至80%以上
测试 demo_generator.py 和 ai_code_generator.py 中未覆盖的代码路径
"""

import sys
import os
import tempfile
import shutil
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_code_generator import (
    CodeGenerationRequest,
    GeneratedFile,
    CodeGenerationResult,
    AICodeGenerator,
    APIProvider,
    APIError,
    main as ai_main
)


class TestDemoGenerator(unittest.TestCase):
    """测试 demo_generator.py 模块"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_demo_template_generation(self):
        """测试演示脚本的主函数"""
        # 导入并运行演示函数
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "demo_generator",
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "demo_generator.py")
        )
        demo_module = importlib.util.module_from_spec(spec)
        
        # 修改输出目录到临时目录
        with patch('sys.stdout') as mock_stdout:
            spec.loader.exec_module(demo_module)
            # 验证函数存在且可调用
            self.assertTrue(hasattr(demo_module, 'demo_template_generation'))
    
    def test_demo_generator_import(self):
        """测试 demo_generator 模块导入"""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "demo_generator",
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "demo_generator.py")
        )
        self.assertIsNotNone(spec)
        demo_module = importlib.util.module_from_spec(spec)
        self.assertIsNotNone(demo_module)


class TestAICodeGeneratorAdvanced(unittest.TestCase):
    """测试 AICodeGenerator 的高级功能"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generate_with_all_frameworks(self):
        """测试所有支持的框架生成"""
        frameworks = ["fastapi", "flask", "django", "express", "react"]
        generator = AICodeGenerator()
        
        for framework in frameworks:
            request = CodeGenerationRequest(
                prompt=f"Create a {framework} app",
                language="python" if framework in ["fastapi", "flask", "django"] else "javascript",
                framework=framework,
                output_dir=self.temp_dir,
                include_tests=True,
                include_docs=True
            )
            
            result = generator.generate(request)
            self.assertTrue(result.success, f"Framework {framework} should generate successfully")
            self.assertGreater(len(result.files), 0)
    
    def test_generate_all_languages(self):
        """测试所有支持的语言生成"""
        languages = ["python", "typescript", "javascript", "go", "rust"]
        generator = AICodeGenerator()
        
        for lang in languages:
            request = CodeGenerationRequest(
                prompt=f"Create a {lang} app",
                language=lang,
                output_dir=self.temp_dir,
                include_tests=True,
                include_docs=True
            )
            
            result = generator.generate(request)
            self.assertTrue(result.success, f"Language {lang} should generate successfully")
    
    def test_save_files_functionality(self):
        """测试保存文件功能"""
        generator = AICodeGenerator()
        request = CodeGenerationRequest(
            prompt="Create a test app",
            language="python",
            output_dir=self.temp_dir
        )
        
        result = generator.generate(request)
        self.assertTrue(result.success)
        
        # 保存文件
        saved_files = generator.save_files(result)
        self.assertGreater(len(saved_files), 0)
        
        # 验证文件存在
        for file_path in saved_files:
            self.assertTrue(Path(file_path).exists())
    
    def test_save_files_custom_output_dir(self):
        """测试使用自定义输出目录保存文件"""
        generator = AICodeGenerator()
        request = CodeGenerationRequest(
            prompt="Create a test app",
            language="python",
            output_dir="/original/path"
        )
        
        result = generator.generate(request)
        custom_dir = os.path.join(self.temp_dir, "custom_output")
        
        saved_files = generator.save_files(result, output_dir=custom_dir)
        
        # 验证文件保存到自定义目录
        for file_path in saved_files:
            self.assertTrue(file_path.startswith(custom_dir))
            self.assertTrue(Path(file_path).exists())
    
    def test_generate_with_ai_api_failure(self):
        """测试AI API失败时回退到模板"""
        generator = AICodeGenerator(api_provider="claude")
        
        # 模拟API客户端存在但调用失败
        generator.api_client = Mock()
        generator.api_client.messages.create.side_effect = Exception("API Error")
        
        request = CodeGenerationRequest(
            prompt="Create a FastAPI app",
            language="python",
            framework="fastapi"
        )
        
        result = generator.generate(request)
        self.assertTrue(result.success)
        self.assertEqual(result.generation_method, "template")
    
    def test_generate_with_ai_empty_response(self):
        """测试AI返回空响应时回退到模板"""
        generator = AICodeGenerator(api_provider="claude")
        generator.api_client = Mock()
        generator.api_client.messages.create.return_value = Mock(content=[Mock(text="")])
        
        request = CodeGenerationRequest(
            prompt="Create a FastAPI app",
            language="python",
            framework="fastapi"
        )
        
        result = generator.generate(request)
        self.assertTrue(result.success)
        self.assertEqual(result.generation_method, "template")
    
    def test_generate_with_ai_parsed_files(self):
        """测试AI生成并解析文件"""
        generator = AICodeGenerator(api_provider="claude")
        generator.api_client = Mock()
        generator.api_key = "test-key"
        
        ai_response = """
=== main.py ===
print("hello world")
=== end ===
=== requirements.txt ===
fastapi
=== end ===
"""
        generator.api_client.messages.create.return_value = Mock(
            content=[Mock(text=ai_response)]
        )
        
        request = CodeGenerationRequest(
            prompt="Create a simple app",
            language="python",
            include_tests=False,
            include_docs=False
        )
        
        result = generator.generate(request)
        self.assertTrue(result.success)
        self.assertEqual(result.generation_method, "ai")
        # AI生成2个文件 + 自动添加的配置文件
        self.assertGreaterEqual(len(result.files), 2)
    
    def test_call_ai_api_with_retries(self):
        """测试API调用重试机制"""
        generator = AICodeGenerator(api_provider="claude")
        generator.api_client = Mock()
        
        # 前两次失败，第三次成功
        generator.api_client.messages.create.side_effect = [
            Exception("Error 1"),
            Exception("Error 2"),
            Mock(content=[Mock(text="Success")])
        ]
        
        result = generator._call_ai_api("test prompt", max_retries=3)
        self.assertEqual(result, "Success")
        self.assertEqual(generator.api_client.messages.create.call_count, 3)
    
    def test_call_ai_api_all_retries_fail(self):
        """测试所有重试都失败的情况"""
        generator = AICodeGenerator(api_provider="claude")
        generator.api_client = Mock()
        generator.api_client.messages.create.side_effect = Exception("API Error")
        
        result = generator._call_ai_api("test prompt", max_retries=2)
        self.assertIsNone(result)
    
    def test_call_ai_api_openai(self):
        """测试 OpenAI API 调用"""
        generator = AICodeGenerator(api_provider="openai")
        generator.api_client = Mock()
        generator.api_key = "test-key"
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Generated code"))]
        generator.api_client.chat.completions.create.return_value = mock_response
        
        result = generator._call_ai_api("test prompt")
        self.assertEqual(result, "Generated code")
    
    def test_call_ai_api_kimi(self):
        """测试 Kimi API 调用"""
        generator = AICodeGenerator(api_provider="kimi")
        generator.api_client = Mock()
        generator.api_key = "test-key"
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Generated code"))]
        generator.api_client.chat.completions.create.return_value = mock_response
        
        result = generator._call_ai_api("test prompt")
        self.assertEqual(result, "Generated code")
    
    def test_parse_ai_response_code_block_format(self):
        """测试解析代码块格式的AI响应"""
        generator = AICodeGenerator()
        
        response = """
Here's the code:
```python
print("hello")
```
"""
        request = CodeGenerationRequest(prompt="test", language="python")
        files = generator._parse_ai_response(response, request)
        
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].path, "main.py")
    
    def test_parse_ai_response_unknown_language(self):
        """测试解析未知语言的AI响应"""
        generator = AICodeGenerator()
        
        response = """
```
some code here
```
"""
        request = CodeGenerationRequest(prompt="test", language="unknown_lang")
        files = generator._parse_ai_response(response, request)
        
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].path, "main.py")  # 默认扩展名
    
    def test_extract_dependencies_from_files(self):
        """测试从文件中提取依赖"""
        generator = AICodeGenerator()
        
        files = [
            GeneratedFile(
                path="requirements.txt",
                content="fastapi>=0.104.0\nuvicorn>=0.24.0\n# comment"
            ),
            GeneratedFile(
                path="package.json",
                content='{"dependencies": {"express": "^4.18.0", "cors": "^2.8.5"}}'
            )
        ]
        
        deps = generator._extract_dependencies_from_files(files, "python")
        self.assertIn("fastapi>=0.104.0", deps)
        self.assertIn("uvicorn>=0.24.0", deps)
    
    def test_extract_dependencies_invalid_json(self):
        """测试从无效JSON中提取依赖"""
        generator = AICodeGenerator()
        
        files = [
            GeneratedFile(
                path="package.json",
                content="invalid json"
            )
        ]
        
        deps = generator._extract_dependencies_from_files(files, "javascript")
        self.assertEqual(len(deps), 0)
    
    def test_analyze_requirements_automation(self):
        """测试分析自动化项目类型"""
        generator = AICodeGenerator()
        
        request = CodeGenerationRequest(
            prompt="Create a web scraper bot",
            language="python"
        )
        
        architecture = generator._analyze_requirements(request)
        self.assertEqual(architecture["project_type"], "automation")
        self.assertEqual(architecture["language"], "python")
    
    def test_estimate_complexity_medium(self):
        """测试中复杂度估计"""
        generator = AICodeGenerator()
        
        # 使用足够长的提示词触发 medium 复杂度
        prompt = "Create a web application with user authentication database support caching layer email service file upload functionality"
        complexity = generator._estimate_complexity(prompt)
        self.assertEqual(complexity, "medium")
    
    def test_generate_api_files_python(self):
        """测试生成Python API文件 - 目前只支持Python"""
        generator = AICodeGenerator()
        
        request = CodeGenerationRequest(
            prompt="Create API",
            language="python",
            framework="fastapi"
        )
        architecture = {"framework": "fastapi", "project_type": "api"}
        
        files = generator._generate_api_files(request, architecture)
        self.assertGreater(len(files), 0)
        paths = [f.path for f in files]
        self.assertIn("main.py", paths)
    
    def test_generate_cli_files_python(self):
        """测试生成Python CLI文件 - 目前只支持Python"""
        generator = AICodeGenerator()
        
        request = CodeGenerationRequest(
            prompt="Create CLI",
            language="python"
        )
        architecture = {"project_type": "cli"}
        
        files = generator._generate_cli_files(request, architecture)
        self.assertGreater(len(files), 0)
        paths = [f.path for f in files]
        self.assertIn("cli.py", paths)
    
    def test_generate_generic_files_all_languages(self):
        """测试为所有语言生成通用文件"""
        generator = AICodeGenerator()
        languages = ["python", "typescript", "javascript", "go", "rust", "unknown"]
        
        for lang in languages:
            request = CodeGenerationRequest(prompt="test", language=lang)
            architecture = {}
            
            files = generator._generate_generic_files(request, architecture)
            self.assertGreater(len(files), 0, f"Language {lang} should generate files")
    
    def test_generate_test_files_python_only(self):
        """测试生成Python测试文件 - 目前只支持Python"""
        generator = AICodeGenerator()
        
        request = CodeGenerationRequest(
            prompt="test",
            language="python",
            include_tests=True
        )
        architecture = {}
        
        files = generator._generate_test_files(request, architecture)
        self.assertGreater(len(files), 0)
        paths = [f.path for f in files]
        self.assertIn("tests/test_main.py", paths)
    
    def test_generate_dependencies_no_framework(self):
        """测试无框架时的依赖生成"""
        generator = AICodeGenerator()
        
        request = CodeGenerationRequest(prompt="test", language="python")
        architecture = {"framework": None}
        
        deps = generator._generate_dependencies(request, architecture)
        self.assertEqual(len(deps), 0)
    
    def test_get_install_command_all_languages(self):
        """测试所有语言的安装命令"""
        generator = AICodeGenerator()
        languages = ["python", "typescript", "javascript", "go", "rust", "unknown"]
        
        for lang in languages:
            cmd = generator._get_install_command(lang)
            if lang in ["python", "typescript", "javascript", "go", "rust"]:
                self.assertTrue(len(cmd) > 0)
    
    def test_get_run_command_all_languages(self):
        """测试所有语言的运行命令"""
        generator = AICodeGenerator()
        languages = ["python", "typescript", "javascript", "go", "rust", "unknown"]
        
        for lang in languages:
            cmd = generator._get_run_command(lang, {})
            if lang in ["python", "typescript", "javascript", "go", "rust"]:
                self.assertTrue(len(cmd) > 0)
    
    def test_generate_setup_instructions_all_languages(self):
        """测试所有语言的设置说明生成"""
        generator = AICodeGenerator()
        languages = ["python", "typescript", "javascript", "go", "rust", "unknown"]
        
        for lang in languages:
            request = CodeGenerationRequest(prompt="test", language=lang)
            architecture = {}
            
            instructions = generator._generate_setup_instructions(request, architecture)
            if lang in ["python", "typescript", "javascript"]:
                self.assertGreater(len(instructions), 0)


class TestAICodeGeneratorMain(unittest.TestCase):
    """测试 ai_code_generator.py 的 main 函数"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('sys.argv', ['ai_code_generator', 'Create a test app', '--language', 'python'])
    def test_main_success(self):
        """测试主函数成功执行"""
        with patch('ai_code_generator.AICodeGenerator') as mock_generator:
            mock_instance = Mock()
            mock_result = Mock()
            mock_result.success = True
            mock_result.files = [Mock()]
            mock_result.generation_method = "template"
            mock_result.api_provider = None
            mock_instance.generate.return_value = mock_result
            mock_instance.save_files.return_value = ["file1.py"]
            mock_generator.return_value = mock_instance
            
            result = ai_main()
            self.assertEqual(result, 0)
    
    @patch('sys.argv', ['ai_code_generator', 'Create a test app'])
    def test_main_failure(self):
        """测试主函数失败情况"""
        with patch('ai_code_generator.AICodeGenerator') as mock_generator:
            mock_instance = Mock()
            mock_result = Mock()
            mock_result.success = False
            mock_result.error = "Generation failed"
            mock_instance.generate.return_value = mock_result
            mock_generator.return_value = mock_instance
            
            result = ai_main()
            self.assertEqual(result, 1)
    
    @patch('sys.argv', ['ai_code_generator', 'Create app', '--framework', 'fastapi', '--no-tests', '--no-docs'])
    def test_main_with_options(self):
        """测试主函数带选项"""
        with patch('ai_code_generator.AICodeGenerator') as mock_generator:
            mock_instance = Mock()
            mock_result = Mock()
            mock_result.success = True
            mock_result.files = []
            mock_result.generation_method = "template"
            mock_instance.generate.return_value = mock_result
            mock_instance.save_files.return_value = []
            mock_generator.return_value = mock_instance
            
            result = ai_main()
            self.assertEqual(result, 0)


class TestAPIProviderEnum(unittest.TestCase):
    """测试 APIProvider 枚举"""
    
    def test_enum_values(self):
        """测试枚举值"""
        self.assertEqual(APIProvider.CLAUDE.value, "claude")
        self.assertEqual(APIProvider.OPENAI.value, "openai")
        self.assertEqual(APIProvider.KIMI.value, "kimi")


class TestAPIError(unittest.TestCase):
    """测试 APIError 异常"""
    
    def test_api_error_creation(self):
        """测试创建 APIError"""
        error = APIError("Test error message")
        self.assertEqual(str(error), "Test error message")


class TestEdgeCasesAdvanced(unittest.TestCase):
    """测试更多边界情况"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_code_generation_request_max_tokens(self):
        """测试请求中的 max_tokens 参数"""
        request = CodeGenerationRequest(
            prompt="test",
            max_tokens=2048,
            temperature=0.5
        )
        self.assertEqual(request.max_tokens, 2048)
        self.assertEqual(request.temperature, 0.5)
    
    def test_generate_with_temperature(self):
        """测试使用 temperature 参数生成"""
        generator = AICodeGenerator()
        generator.api_client = Mock()
        generator.api_key = "test"
        
        mock_response = Mock()
        mock_response.content = [Mock(text="=== main.py ===\nprint(1)\n=== end ===")]
        generator.api_client.messages.create.return_value = mock_response
        
        request = CodeGenerationRequest(
            prompt="test",
            temperature=0.7,
            max_tokens=2048
        )
        
        result = generator.generate(request)
        # 验证API调用使用了正确的参数
        call_kwargs = generator.api_client.messages.create.call_args[1]
        self.assertEqual(call_kwargs['temperature'], 0.7)
        self.assertEqual(call_kwargs['max_tokens'], 2048)
    
    def test_generate_web_files_typescript(self):
        """测试生成 TypeScript Web 文件"""
        generator = AICodeGenerator()
        
        request = CodeGenerationRequest(
            prompt="Create web app",
            language="typescript"
        )
        architecture = {"project_type": "web"}
        
        files = generator._generate_web_files(request, architecture)
        self.assertGreater(len(files), 0)
        self.assertEqual(files[0].path, "index.html")
    
    def test_generate_doc_files_content(self):
        """测试生成文档文件内容"""
        generator = AICodeGenerator()
        
        request = CodeGenerationRequest(
            prompt="Create a special application",
            language="python",
            include_docs=True
        )
        architecture = {}
        
        files = generator._generate_doc_files(request, architecture)
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].path, "README.md")
        self.assertIn("special application", files[0].content)
    
    def test_generate_config_files_content(self):
        """测试生成配置文件内容"""
        generator = AICodeGenerator()
        
        request = CodeGenerationRequest(prompt="test", language="python")
        architecture = {}
        
        files = generator._generate_config_files(request, architecture)
        paths = [f.path for f in files]
        
        self.assertIn(".gitignore", paths)
        self.assertIn(".env.example", paths)
        
        # 验证内容
        gitignore_file = next(f for f in files if f.path == ".gitignore")
        self.assertIn("__pycache__/", gitignore_file.content)

    def test_init_api_client_import_error(self):
        """测试API客户端初始化时ImportError处理"""
        # 模拟 anthropic 包未安装
        with patch.dict('sys.modules', {'anthropic': None}):
            with patch.object(AICodeGenerator, '_get_api_key', return_value="test-key"):
                generator = AICodeGenerator(api_provider="claude")
                # 由于无法导入anthropic，api_client应该为None
                self.assertIsNone(generator.api_client)

    def test_init_api_client_openai_import_error(self):
        """测试OpenAI API客户端初始化时ImportError处理"""
        with patch.dict('sys.modules', {'openai': None}):
            with patch.object(AICodeGenerator, '_get_api_key', return_value="test-key"):
                generator = AICodeGenerator(api_provider="openai")
                self.assertIsNone(generator.api_client)

    def test_init_api_client_kimi_import_error(self):
        """测试Kimi API客户端初始化时ImportError处理"""
        with patch.dict('sys.modules', {'openai': None}):
            with patch.object(AICodeGenerator, '_get_api_key', return_value="test-key"):
                generator = AICodeGenerator(api_provider="kimi")
                self.assertIsNone(generator.api_client)

    def test_generate_exception_handling(self):
        """测试生成过程中的异常处理"""
        generator = AICodeGenerator()
        
        # 模拟 _analyze_requirements 抛出异常
        with patch.object(generator, '_analyze_requirements', side_effect=Exception("Test error")):
            request = CodeGenerationRequest(prompt="test", language="python")
            result = generator.generate(request)
            
            self.assertFalse(result.success)
            self.assertEqual(result.generation_method, "failed")
            self.assertIn("Test error", result.error)

    def test_generate_with_ai_no_gitignore(self):
        """测试AI生成时没有.gitignore的情况"""
        generator = AICodeGenerator(api_provider="claude")
        generator.api_client = Mock()
        generator.api_key = "test-key"
        
        # AI响应不包含.gitignore
        ai_response = """
=== main.py ===
print("hello")
=== end ===
"""
        generator.api_client.messages.create.return_value = Mock(
            content=[Mock(text=ai_response)]
        )
        
        request = CodeGenerationRequest(prompt="test", language="python")
        architecture = {"project_type": "generic"}
        
        result = generator._generate_with_ai(request, architecture)
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
        # 验证自动添加了.gitignore
        paths = [f.path for f in result.files]
        self.assertIn(".gitignore", paths)

    def test_generate_with_ai_returns_none(self):
        """测试AI生成返回None时的情况"""
        generator = AICodeGenerator(api_provider="claude")
        generator.api_client = Mock()
        generator.api_key = "test-key"
        
        # 模拟API返回空响应
        generator.api_client.messages.create.return_value = Mock(
            content=[Mock(text="")]
        )
        
        request = CodeGenerationRequest(prompt="test", language="python")
        architecture = {"project_type": "generic"}
        
        result = generator._generate_with_ai(request, architecture)
        # 当AI返回空时，应该返回None，让generate方法回退到模板
        self.assertIsNone(result)

    def test_analyze_requirements_flask_framework(self):
        """测试分析Flask框架"""
        generator = AICodeGenerator()
        request = CodeGenerationRequest(
            prompt="Create a flask web application",
            language="python"
        )
        architecture = generator._analyze_requirements(request)
        self.assertEqual(architecture["framework"], "flask")

    def test_analyze_requirements_django_framework(self):
        """测试分析Django框架"""
        generator = AICodeGenerator()
        request = CodeGenerationRequest(
            prompt="Build a django website",
            language="python"
        )
        architecture = generator._analyze_requirements(request)
        self.assertEqual(architecture["framework"], "django")

    def test_analyze_requirements_express_framework(self):
        """测试分析Express框架"""
        generator = AICodeGenerator()
        request = CodeGenerationRequest(
            prompt="Create an express server",
            language="javascript"
        )
        architecture = generator._analyze_requirements(request)
        self.assertEqual(architecture["framework"], "express")

    def test_analyze_requirements_react_framework(self):
        """测试分析React框架"""
        generator = AICodeGenerator()
        request = CodeGenerationRequest(
            prompt="Build a react application",
            language="javascript"
        )
        architecture = generator._analyze_requirements(request)
        self.assertEqual(architecture["framework"], "react")

    def test_generate_files_with_web_project(self):
        """测试生成Web项目文件"""
        generator = AICodeGenerator()
        request = CodeGenerationRequest(
            prompt="Create a web app",
            language="python",
            include_tests=True,
            include_docs=True
        )
        architecture = {"project_type": "web"}
        
        files = generator._generate_files(request, architecture)
        self.assertGreater(len(files), 0)

    def test_main_with_save_error(self):
        """测试main函数保存文件失败的情况"""
        with patch('sys.argv', ['ai_code_generator', 'Create app']):
            with patch('ai_code_generator.AICodeGenerator') as mock_generator:
                mock_instance = Mock()
                mock_result = Mock()
                mock_result.success = True
                mock_result.files = [Mock()]
                mock_result.generation_method = "template"
                mock_result.api_provider = None
                mock_instance.generate.return_value = mock_result
                # 模拟保存失败返回空列表
                mock_instance.save_files.return_value = []
                mock_generator.return_value = mock_instance
                
                result = ai_main()
                self.assertEqual(result, 0)


def run_tests():
    """运行所有补充测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        TestDemoGenerator,
        TestAICodeGeneratorAdvanced,
        TestAICodeGeneratorMain,
        TestAPIProviderEnum,
        TestAPIError,
        TestEdgeCasesAdvanced
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
