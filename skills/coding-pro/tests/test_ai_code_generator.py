#!/usr/bin/env python3
"""
Test suite for coding-pro ai_code_generator module
Tests the AI-powered code generation functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import Mock, patch, MagicMock
from ai_code_generator import (
    CodeGenerationRequest,
    GeneratedFile,
    CodeGenerationResult,
    AICodeGenerator,
    main
)


class TestCodeGenerationRequest(unittest.TestCase):
    """Test CodeGenerationRequest dataclass"""
    
    def test_default_values(self):
        """Test default values"""
        request = CodeGenerationRequest(prompt="Generate a function")
        
        self.assertEqual(request.prompt, "Generate a function")
        self.assertEqual(request.language, "python")
        self.assertIsNone(request.framework)
        self.assertEqual(request.output_dir, "./generated")
        self.assertTrue(request.include_tests)
        self.assertTrue(request.include_docs)
    
    def test_custom_values(self):
        """Test custom values"""
        request = CodeGenerationRequest(
            prompt="Create API",
            language="typescript",
            framework="express",
            output_dir="./output",
            include_tests=False,
            include_docs=False
        )
        
        self.assertEqual(request.language, "typescript")
        self.assertEqual(request.framework, "express")
        self.assertEqual(request.output_dir, "./output")
        self.assertFalse(request.include_tests)
        self.assertFalse(request.include_docs)


class TestGeneratedFile(unittest.TestCase):
    """Test GeneratedFile dataclass"""
    
    def test_file_creation(self):
        """Test creating a GeneratedFile"""
        file = GeneratedFile(
            path="main.py",
            content="print('hello')",
            description="Main file"
        )
        
        self.assertEqual(file.path, "main.py")
        self.assertEqual(file.content, "print('hello')")
        self.assertEqual(file.description, "Main file")


class TestCodeGenerationResult(unittest.TestCase):
    """Test CodeGenerationResult dataclass"""
    
    def test_success_result(self):
        """Test successful result"""
        request = CodeGenerationRequest(prompt="test")
        result = CodeGenerationResult(
            success=True,
            request=request,
            files=[],
            architecture={"type": "api"},
            dependencies=["fastapi"],
            setup_instructions=["pip install"]
        )
        
        self.assertTrue(result.success)
        self.assertIsNone(result.error)
    
    def test_failed_result(self):
        """Test failed result"""
        request = CodeGenerationRequest(prompt="test")
        result = CodeGenerationResult(
            success=False,
            request=request,
            files=[],
            architecture={},
            dependencies=[],
            setup_instructions=[],
            error="Generation failed"
        )
        
        self.assertFalse(result.success)
        self.assertEqual(result.error, "Generation failed")


class TestAICodeGenerator(unittest.TestCase):
    """Test AICodeGenerator class"""
    
    def setUp(self):
        self.generator = AICodeGenerator(api_provider="claude")
    
    def test_init_default(self):
        """Test default initialization"""
        gen = AICodeGenerator()
        self.assertEqual(gen.api_provider, "claude")
    
    def test_init_custom_provider(self):
        """Test initialization with custom provider"""
        gen = AICodeGenerator(api_provider="openai")
        self.assertEqual(gen.api_provider, "openai")
    
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_get_api_key_claude(self):
        """Test getting Claude API key"""
        gen = AICodeGenerator(api_provider="claude")
        self.assertEqual(gen.api_key, "test-key")
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "openai-key"})
    def test_get_api_key_openai(self):
        """Test getting OpenAI API key"""
        gen = AICodeGenerator(api_provider="openai")
        self.assertEqual(gen.api_key, "openai-key")
    
    @patch.dict(os.environ, {"KIMI_API_KEY": "kimi-key"})
    def test_get_api_key_kimi(self):
        """Test getting Kimi API key"""
        gen = AICodeGenerator(api_provider="kimi")
        self.assertEqual(gen.api_key, "kimi-key")
    
    def test_get_api_key_not_found(self):
        """Test when API key is not found"""
        with patch.dict(os.environ, {}, clear=True):
            gen = AICodeGenerator(api_provider="claude")
            self.assertIsNone(gen.api_key)
    
    def test_analyze_requirements_api(self):
        """Test analyzing API requirements"""
        request = CodeGenerationRequest(
            prompt="Create a REST API with endpoints",
            language="python"
        )
        
        architecture = self.generator._analyze_requirements(request)
        
        self.assertEqual(architecture["project_type"], "api")
        self.assertEqual(architecture["language"], "python")
    
    def test_analyze_requirements_cli(self):
        """Test analyzing CLI requirements"""
        request = CodeGenerationRequest(
            prompt="Create a command line tool",
            language="python"
        )
        
        architecture = self.generator._analyze_requirements(request)
        
        self.assertEqual(architecture["project_type"], "cli")
    
    def test_analyze_requirements_web(self):
        """Test analyzing web requirements"""
        request = CodeGenerationRequest(
            prompt="Build a website frontend",
            language="typescript"
        )
        
        architecture = self.generator._analyze_requirements(request)
        
        self.assertEqual(architecture["project_type"], "web")
    
    def test_analyze_requirements_with_framework(self):
        """Test analyzing with explicit framework"""
        request = CodeGenerationRequest(
            prompt="Create API",
            language="python",
            framework="fastapi"
        )
        
        architecture = self.generator._analyze_requirements(request)
        
        self.assertEqual(architecture["framework"], "fastapi")
    
    def test_analyze_requirements_infer_fastapi(self):
        """Test inferring FastAPI from prompt"""
        request = CodeGenerationRequest(
            prompt="Create a FastAPI application",
            language="python"
        )
        
        architecture = self.generator._analyze_requirements(request)
        
        self.assertEqual(architecture["framework"], "fastapi")
    
    def test_extract_features_auth(self):
        """Test extracting auth feature"""
        features = self.generator._extract_features("Add user login and JWT authentication")
        self.assertIn("auth", features)
    
    def test_extract_features_database(self):
        """Test extracting database feature"""
        features = self.generator._extract_features("Connect to PostgreSQL database")
        self.assertIn("database", features)
    
    def test_extract_features_multiple(self):
        """Test extracting multiple features"""
        features = self.generator._extract_features(
            "Create API with auth, database, and Redis cache"
        )
        self.assertIn("auth", features)
        self.assertIn("database", features)
        self.assertIn("cache", features)
    
    def test_estimate_complexity_high(self):
        """Test high complexity estimation"""
        complexity = self.generator._estimate_complexity(
            "Create a comprehensive full-featured enterprise-grade e-commerce platform with user authentication, "
            "secure payment processing, advanced inventory management, real-time notifications, "
            "powerful admin dashboard, multi-language internationalization support, advanced search and filtering features, "
            "AI-powered recommendations engine, extensive social media integration, detailed analytics dashboard, "
            "native mobile app support, extensive third-party API integrations, blockchain payment support, "
            "custom machine learning models, high-quality video streaming capabilities, comprehensive IoT device management, "
            "and enterprise-grade security features"
        )
        self.assertEqual(complexity, "high")
    
    def test_estimate_complexity_low(self):
        """Test low complexity estimation"""
        complexity = self.generator._estimate_complexity("Simple hello world")
        self.assertEqual(complexity, "low")
    
    def test_generate_api_files_python(self):
        """Test generating Python API files"""
        request = CodeGenerationRequest(
            prompt="Create API",
            language="python",
            framework="fastapi"
        )
        architecture = {"framework": "fastapi", "project_type": "api"}
        
        files = self.generator._generate_api_files(request, architecture)
        
        paths = [f.path for f in files]
        self.assertIn("main.py", paths)
        self.assertIn("requirements.txt", paths)
    
    def test_generate_cli_files(self):
        """Test generating CLI files"""
        request = CodeGenerationRequest(
            prompt="Create CLI tool",
            language="python"
        )
        architecture = {"project_type": "cli"}
        
        files = self.generator._generate_cli_files(request, architecture)
        
        paths = [f.path for f in files]
        self.assertIn("cli.py", paths)
    
    def test_generate_web_files(self):
        """Test generating web files"""
        request = CodeGenerationRequest(
            prompt="Create website",
            language="javascript"
        )
        architecture = {"project_type": "web"}
        
        files = self.generator._generate_web_files(request, architecture)
        
        paths = [f.path for f in files]
        self.assertIn("index.html", paths)
    
    def test_generate_config_files(self):
        """Test generating config files"""
        request = CodeGenerationRequest(prompt="test")
        architecture = {}
        
        files = self.generator._generate_config_files(request, architecture)
        
        paths = [f.path for f in files]
        self.assertIn(".gitignore", paths)
        self.assertIn(".env.example", paths)
    
    def test_generate_test_files_python(self):
        """Test generating Python test files"""
        request = CodeGenerationRequest(
            prompt="test",
            language="python",
            include_tests=True
        )
        architecture = {}
        
        files = self.generator._generate_test_files(request, architecture)
        
        paths = [f.path for f in files]
        self.assertIn("tests/test_main.py", paths)
    
    def test_generate_doc_files(self):
        """Test generating documentation files"""
        request = CodeGenerationRequest(
            prompt="Create a simple app",
            language="python",
            include_docs=True
        )
        architecture = {}
        
        files = self.generator._generate_doc_files(request, architecture)
        
        paths = [f.path for f in files]
        self.assertIn("README.md", paths)
    
    def test_generate_dependencies_fastapi(self):
        """Test generating FastAPI dependencies"""
        request = CodeGenerationRequest(
            prompt="Create API",
            language="python",
            framework="fastapi"
        )
        architecture = {"framework": "fastapi", "language": "python"}
        
        deps = self.generator._generate_dependencies(request, architecture)
        
        self.assertIn("fastapi>=0.104.0", deps)
        self.assertIn("uvicorn[standard]>=0.24.0", deps)
    
    def test_generate_dependencies_flask(self):
        """Test generating Flask dependencies"""
        request = CodeGenerationRequest(
            prompt="Create web app",
            language="python",
            framework="flask"
        )
        architecture = {"framework": "flask", "language": "python"}
        
        deps = self.generator._generate_dependencies(request, architecture)
        
        self.assertIn("flask>=3.0.0", deps)
    
    def test_get_install_command_python(self):
        """Test getting Python install command"""
        cmd = self.generator._get_install_command("python")
        self.assertEqual(cmd, "pip install -r requirements.txt")
    
    def test_get_install_command_javascript(self):
        """Test getting JavaScript install command"""
        cmd = self.generator._get_install_command("javascript")
        self.assertEqual(cmd, "npm install")
    
    def test_get_run_command_python(self):
        """Test getting Python run command"""
        cmd = self.generator._get_run_command("python", {})
        self.assertEqual(cmd, "python main.py")
    
    def test_parse_ai_response_with_format(self):
        """Test parsing AI response with === format"""
        response = """
=== main.py ===
print("hello")
=== end ===
=== README.md ===
# Project
=== end ===
"""
        request = CodeGenerationRequest(prompt="test")
        
        files = self.generator._parse_ai_response(response, request)
        
        self.assertEqual(len(files), 2)
        self.assertEqual(files[0].path, "main.py")
        self.assertEqual(files[1].path, "README.md")
    
    def test_parse_ai_response_code_block(self):
        """Test parsing AI response with code block"""
        response = """
Here's the code:
```python
print("hello")
```
"""
        request = CodeGenerationRequest(
            prompt="test",
            language="python"
        )
        
        files = self.generator._parse_ai_response(response, request)
        
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].path, "main.py")
    
    def test_generate_setup_instructions(self):
        """Test generating setup instructions"""
        request = CodeGenerationRequest(
            prompt="test",
            language="python"
        )
        architecture = {}
        
        instructions = self.generator._generate_setup_instructions(request, architecture)
        
        self.assertEqual(len(instructions), 2)
        self.assertIn("pip install", instructions[0])
        self.assertIn("python main.py", instructions[1])
    
    def test_generate_success(self):
        """Test successful generation"""
        request = CodeGenerationRequest(
            prompt="Create a simple Python script",
            language="python"
        )
        
        result = self.generator.generate(request)
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.files)
        self.assertIsNotNone(result.architecture)
    
    def test_language_templates(self):
        """Test language templates are defined"""
        self.assertIn("python", self.generator.LANGUAGE_TEMPLATES)
        self.assertIn("typescript", self.generator.LANGUAGE_TEMPLATES)
        self.assertIn("javascript", self.generator.LANGUAGE_TEMPLATES)
        self.assertIn("go", self.generator.LANGUAGE_TEMPLATES)
        self.assertIn("rust", self.generator.LANGUAGE_TEMPLATES)
    
    def test_framework_templates(self):
        """Test framework templates are defined"""
        self.assertIn("fastapi", self.generator.FRAMEWORK_TEMPLATES)
        self.assertIn("flask", self.generator.FRAMEWORK_TEMPLATES)
        self.assertIn("django", self.generator.FRAMEWORK_TEMPLATES)
        self.assertIn("express", self.generator.FRAMEWORK_TEMPLATES)
        self.assertIn("react", self.generator.FRAMEWORK_TEMPLATES)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_generation_flow(self):
        """Test full generation flow"""
        request = CodeGenerationRequest(
            prompt="Create a FastAPI application",
            language="python",
            framework="fastapi",
            include_tests=True,
            include_docs=True
        )
        
        generator = AICodeGenerator()
        result = generator.generate(request)
        
        self.assertTrue(result.success)
        self.assertGreater(len(result.files), 0)
        self.assertIn("project_type", result.architecture)
        self.assertIn("framework", result.architecture)
    
    def test_generation_without_tests(self):
        """Test generation without tests"""
        request = CodeGenerationRequest(
            prompt="Create a script",
            language="python",
            include_tests=False
        )
        
        generator = AICodeGenerator()
        result = generator.generate(request)
        
        self.assertTrue(result.success)
        test_files = [f for f in result.files if "test" in f.path]
        self.assertEqual(len(test_files), 0)


def run_tests():
    """Run all tests and return results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        TestCodeGenerationRequest,
        TestGeneratedFile,
        TestCodeGenerationResult,
        TestAICodeGenerator,
        TestIntegration
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
