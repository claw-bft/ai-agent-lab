#!/usr/bin/env python3
"""
AI Code Generator - 智能代码生成模块
集成Claude API实现自然语言到代码的转换
"""

import os
import json
import re
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum


class APIProvider(Enum):
    """支持的AI API提供商"""
    CLAUDE = "claude"
    OPENAI = "openai"
    KIMI = "kimi"


@dataclass
class CodeGenerationRequest:
    """代码生成请求"""
    prompt: str
    language: str = "python"
    framework: Optional[str] = None
    output_dir: str = "./generated"
    include_tests: bool = True
    include_docs: bool = True
    max_tokens: int = 4096
    temperature: float = 0.2


@dataclass
class GeneratedFile:
    """生成的文件"""
    path: str
    content: str
    description: str = ""


@dataclass
class CodeGenerationResult:
    """代码生成结果"""
    success: bool
    request: CodeGenerationRequest
    files: List[GeneratedFile]
    architecture: Dict[str, Any]
    dependencies: List[str]
    setup_instructions: List[str]
    generation_method: str = "template"  # "ai" or "template"
    api_provider: Optional[str] = None
    error: Optional[str] = None


class APIError(Exception):
    """API调用错误"""
    pass


class AICodeGenerator:
    """AI代码生成器 - 支持真实AI模型API"""
    
    # 语言模板映射
    LANGUAGE_TEMPLATES = {
        "python": {
            "extension": ".py",
            "shebang": "#!/usr/bin/env python3",
            "doc_style": '"""',
            "package_file": "requirements.txt",
            "test_framework": "pytest"
        },
        "typescript": {
            "extension": ".ts",
            "shebang": "",
            "doc_style": "///",
            "package_file": "package.json",
            "test_framework": "jest"
        },
        "javascript": {
            "extension": ".js",
            "shebang": "#!/usr/bin/env node",
            "doc_style": "///",
            "package_file": "package.json",
            "test_framework": "jest"
        },
        "go": {
            "extension": ".go",
            "shebang": "",
            "doc_style": "//",
            "package_file": "go.mod",
            "test_framework": "go test"
        },
        "rust": {
            "extension": ".rs",
            "shebang": "",
            "doc_style": "///",
            "package_file": "Cargo.toml",
            "test_framework": "cargo test"
        }
    }
    
    # 框架模板
    FRAMEWORK_TEMPLATES = {
        "fastapi": {
            "dependencies": ["fastapi", "uvicorn", "pydantic"],
            "structure": ["main.py", "models.py", "routers/", "services/", "config.py"]
        },
        "flask": {
            "dependencies": ["flask", "flask-sqlalchemy", "flask-migrate"],
            "structure": ["app.py", "models.py", "routes.py", "config.py", "templates/"]
        },
        "django": {
            "dependencies": ["django", "djangorestframework"],
            "structure": ["manage.py", "project/", "apps/", "templates/"]
        },
        "express": {
            "dependencies": ["express", "cors", "dotenv"],
            "structure": ["server.js", "routes/", "models/", "middleware/", "config/"]
        },
        "react": {
            "dependencies": ["react", "react-dom", "@vitejs/plugin-react"],
            "structure": ["src/", "public/", "components/", "hooks/", "utils/"]
        }
    }
    
    def __init__(self, api_provider: str = "claude"):
        """
        初始化代码生成器
        
        Args:
            api_provider: AI模型提供商 (claude, openai, kimi)
        """
        self.api_provider = api_provider.lower()
        self.api_key = self._get_api_key()
        self.api_client = None
        self._init_api_client()
    
    def _get_api_key(self) -> Optional[str]:
        """获取API密钥"""
        env_vars = {
            "claude": ["ANTHROPIC_API_KEY", "CLAUDE_API_KEY"],
            "openai": ["OPENAI_API_KEY"],
            "kimi": ["KIMI_API_KEY", "MOONSHOT_API_KEY"]
        }
        
        for var in env_vars.get(self.api_provider, []):
            key = os.getenv(var)
            if key:
                return key
        return None
    
    def _init_api_client(self):
        """初始化API客户端"""
        if self.api_provider == "claude":
            try:
                import anthropic
                if self.api_key:
                    self.api_client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                pass
        elif self.api_provider == "openai":
            try:
                import openai
                if self.api_key:
                    self.api_client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                pass
        elif self.api_provider == "kimi":
            try:
                import openai
                if self.api_key:
                    self.api_client = openai.OpenAI(
                        api_key=self.api_key,
                        base_url="https://api.moonshot.cn/v1"
                    )
            except ImportError:
                pass
    
    def _call_ai_api(self, prompt: str, max_retries: int = 3, request: Optional[CodeGenerationRequest] = None) -> Optional[str]:
        """
        调用AI API生成代码
        
        Args:
            prompt: 生成提示
            max_retries: 最大重试次数
            request: 代码生成请求（用于获取temperature等参数）
            
        Returns:
            生成的代码内容，失败返回None
        """
        if not self.api_client:
            return None
        
        max_tokens = request.max_tokens if request else 4096
        temperature = request.temperature if request else 0.2
        
        system_prompt = """You are an expert software engineer. Generate clean, production-ready code based on the user's requirements.

Rules:
1. Generate complete, working code
2. Include proper error handling
3. Add meaningful comments
4. Follow best practices for the specified language/framework
5. Return ONLY the code, no explanations unless requested

When generating multiple files, use this format:
=== filename.ext ===
<file content>
=== end ==="""

        for attempt in range(max_retries):
            try:
                if self.api_provider == "claude":
                    response = self.api_client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=max_tokens,
                        temperature=temperature,
                        system=system_prompt,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    return response.content[0].text
                    
                elif self.api_provider in ["openai", "kimi"]:
                    model = "gpt-4" if self.api_provider == "openai" else "moonshot-v1-128k"
                    response = self.api_client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    return response.choices[0].message.content
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    time.sleep(wait_time)
                    continue
                print(f"API call failed after {max_retries} attempts: {e}")
                return None
        
        return None
    
    def generate(self, request: CodeGenerationRequest) -> CodeGenerationResult:
        """
        根据请求生成代码
        
        优先使用AI API，失败时回退到模板生成
        """
        try:
            # 分析需求
            architecture = self._analyze_requirements(request)
            
            # 尝试使用AI API生成
            if self.api_client and self.api_key:
                ai_result = self._generate_with_ai(request, architecture)
                if ai_result:
                    return ai_result
            
            # 回退到模板生成
            files = self._generate_files(request, architecture)
            dependencies = self._generate_dependencies(request, architecture)
            setup_instructions = self._generate_setup_instructions(request, architecture)
            
            return CodeGenerationResult(
                success=True,
                request=request,
                files=files,
                architecture=architecture,
                dependencies=dependencies,
                setup_instructions=setup_instructions,
                generation_method="template"
            )
            
        except Exception as e:
            return CodeGenerationResult(
                success=False,
                request=request,
                files=[],
                architecture={},
                dependencies=[],
                setup_instructions=[],
                generation_method="failed",
                error=str(e)
            )
    
    def _generate_with_ai(self, request: CodeGenerationRequest, architecture: Dict[str, Any]) -> Optional[CodeGenerationResult]:
        """使用AI API生成代码"""
        
        prompt = f"""Generate a complete {request.language} project for the following requirement:

{request.prompt}

Framework: {architecture.get('framework', 'None')}
Project Type: {architecture.get('project_type', 'generic')}
Features needed: {', '.join(architecture.get('features', []))}

Generate the following files:
1. Main application file(s)
2. {'Test files' if request.include_tests else 'No tests needed'}
3. {'Documentation (README.md)' if request.include_docs else 'No docs needed'}
4. Configuration files (.gitignore, .env.example)
5. Dependency file (requirements.txt, package.json, etc.)

Use the === filename.ext === format for each file."""

        ai_response = self._call_ai_api(prompt, request=request)
        if not ai_response:
            return None
        
        # 解析AI响应，提取文件
        files = self._parse_ai_response(ai_response, request)
        
        # 如果没有解析到文件，回退到模板
        if not files:
            return None
        
        # 确保有基本配置文件
        existing_paths = {f.path for f in files}
        if ".gitignore" not in existing_paths:
            files.extend(self._generate_config_files(request, architecture))
        
        dependencies = self._extract_dependencies_from_files(files, request.language)
        setup_instructions = self._generate_setup_instructions(request, architecture)
        
        return CodeGenerationResult(
            success=True,
            request=request,
            files=files,
            architecture=architecture,
            dependencies=dependencies,
            setup_instructions=setup_instructions,
            generation_method="ai",
            api_provider=self.api_provider
        )
    
    def _parse_ai_response(self, response: str, request: CodeGenerationRequest) -> List[GeneratedFile]:
        """解析AI响应，提取文件内容"""
        files = []
        
        # 匹配 === filename.ext === 格式
        pattern = r'===\s*(.+?)\s*===\n(.*?)===\s*end\s*==='
        matches = re.findall(pattern, response, re.DOTALL)
        
        for filename, content in matches:
            files.append(GeneratedFile(
                path=filename.strip(),
                content=content.strip(),
                description=f"Generated {filename.strip()}"
            ))
        
        # 如果没有匹配到格式，尝试其他解析方式
        if not files:
            # 尝试匹配代码块
            code_block_pattern = r'```(\w*)\n(.*?)```'
            code_blocks = re.findall(code_block_pattern, response, re.DOTALL)
            
            if code_blocks:
                ext = self.LANGUAGE_TEMPLATES.get(request.language, {}).get("extension", ".py")
                files.append(GeneratedFile(
                    path=f"main{ext}",
                    content=code_blocks[0][1].strip(),
                    description="Generated main file"
                ))
        
        return files
    
    def _extract_dependencies_from_files(self, files: List[GeneratedFile], language: str) -> List[str]:
        """从生成的文件中提取依赖"""
        deps = []
        
        for file in files:
            if file.path == "requirements.txt":
                deps.extend([line.strip() for line in file.content.split('\n') if line.strip() and not line.startswith('#')])
            elif file.path == "package.json":
                try:
                    pkg = json.loads(file.content)
                    deps.extend([f"{k}@{v}" for k, v in pkg.get('dependencies', {}).items()])
                except:
                    pass
        
        return deps
    
    def _analyze_requirements(self, request: CodeGenerationRequest) -> Dict[str, Any]:
        """分析需求并确定架构"""
        prompt_lower = request.prompt.lower()
        
        # 推断项目类型
        if any(kw in prompt_lower for kw in ["api", "rest", "endpoint", "service"]):
            project_type = "api"
        elif any(kw in prompt_lower for kw in ["cli", "command", "tool", "script"]):
            project_type = "cli"
        elif any(kw in prompt_lower for kw in ["web", "website", "frontend", "ui"]):
            project_type = "web"
        elif any(kw in prompt_lower for kw in ["bot", "automation", "scraper", "crawler"]):
            project_type = "automation"
        else:
            project_type = "generic"
        
        # 推断框架
        framework = request.framework
        if not framework:
            if request.language == "python":
                if "fastapi" in prompt_lower:
                    framework = "fastapi"
                elif "flask" in prompt_lower:
                    framework = "flask"
                elif "django" in prompt_lower:
                    framework = "django"
                elif project_type == "api":
                    framework = "fastapi"
            elif request.language in ["typescript", "javascript"]:
                if "express" in prompt_lower:
                    framework = "express"
                elif "react" in prompt_lower:
                    framework = "react"
        
        return {
            "project_type": project_type,
            "framework": framework,
            "language": request.language,
            "features": self._extract_features(prompt_lower),
            "complexity": self._estimate_complexity(request.prompt)
        }
    
    def _extract_features(self, prompt: str) -> List[str]:
        """从提示中提取功能特征"""
        features = []
        feature_keywords = {
            "auth": ["auth", "login", "logout", "jwt", "token", "password", "oauth"],
            "database": ["database", "db", "sql", "mongodb", "postgres", "mysql", "sqlite"],
            "cache": ["cache", "redis", "memcached"],
            "queue": ["queue", "worker", "celery", "rabbitmq", "kafka"],
            "email": ["email", "mail", "smtp", "notification"],
            "upload": ["upload", "file", "image", "storage", "s3"],
            "payment": ["payment", "stripe", "paypal", "billing"],
            "search": ["search", "elasticsearch", "algolia"],
            "websocket": ["websocket", "socket", "realtime", "live"],
            "testing": ["test", "pytest", "unittest", "jest"]
        }
        
        for feature, keywords in feature_keywords.items():
            if any(kw in prompt for kw in keywords):
                features.append(feature)
        
        return features
    
    def _estimate_complexity(self, prompt: str) -> str:
        """估计项目复杂度"""
        word_count = len(prompt.split())
        feature_count = len(self._extract_features(prompt.lower()))
        
        if word_count > 50 or feature_count > 5:
            return "high"
        elif word_count > 20 or feature_count > 2:
            return "medium"
        return "low"
    
    def _generate_files(self, request: CodeGenerationRequest, architecture: Dict[str, Any]) -> List[GeneratedFile]:
        """生成项目文件 (模板方式)"""
        files = []
        lang = request.language
        framework = architecture.get("framework")
        project_type = architecture.get("project_type")
        
        if project_type == "api":
            files.extend(self._generate_api_files(request, architecture))
        elif project_type == "cli":
            files.extend(self._generate_cli_files(request, architecture))
        elif project_type == "web":
            files.extend(self._generate_web_files(request, architecture))
        else:
            files.extend(self._generate_generic_files(request, architecture))
        
        files.extend(self._generate_config_files(request, architecture))
        
        if request.include_tests:
            files.extend(self._generate_test_files(request, architecture))
        
        if request.include_docs:
            files.extend(self._generate_doc_files(request, architecture))
        
        return files
    
    def _generate_api_files(self, request: CodeGenerationRequest, architecture: Dict[str, Any]) -> List[GeneratedFile]:
        """生成API项目文件"""
        files = []
        lang = request.language
        framework = architecture.get("framework")
        
        if lang == "python" and framework == "fastapi":
            files.append(GeneratedFile(
                path="main.py",
                description="FastAPI应用入口",
                content='''#!/usr/bin/env python3
"""FastAPI Application - Generated by AI Code Generator"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

app = FastAPI(title="API Service", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to API Service", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
            ))
            
            files.append(GeneratedFile(
                path="requirements.txt",
                description="Python依赖",
                content='''fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
'''
            ))
        
        return files
    
    def _generate_cli_files(self, request: CodeGenerationRequest, architecture: Dict[str, Any]) -> List[GeneratedFile]:
        """生成CLI项目文件"""
        files = []
        lang = request.language
        
        if lang == "python":
            files.append(GeneratedFile(
                path="cli.py",
                description="CLI工具入口",
                content='''#!/usr/bin/env python3
"""CLI Tool - Generated by AI Code Generator"""

import argparse
import sys

def main():
    parser = argparse.ArgumentParser(prog="cli-tool")
    parser.add_argument("--version", action="version", version="1.0.0")
    args = parser.parse_args()

if __name__ == "__main__":
    main()
'''
            ))
        
        return files
    
    def _generate_web_files(self, request: CodeGenerationRequest, architecture: Dict[str, Any]) -> List[GeneratedFile]:
        """生成Web项目文件"""
        files = []
        
        files.append(GeneratedFile(
            path="index.html",
            description="HTML入口",
            content='''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Application</title>
</head>
<body>
    <div id="app">
        <h1>Welcome</h1>
        <p>Generated by AI Code Generator</p>
    </div>
</body>
</html>
'''
        ))
        
        return files
    
    def _generate_generic_files(self, request: CodeGenerationRequest, architecture: Dict[str, Any]) -> List[GeneratedFile]:
        """生成通用项目文件"""
        files = []
        lang = request.language
        lang_config = self.LANGUAGE_TEMPLATES.get(lang, {})
        ext = lang_config.get("extension", ".py")
        shebang = lang_config.get("shebang", "")
        
        if lang == "python":
            content = f'''{shebang}
"""Generated Module - AI Code Generator"""

def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
'''
        else:
            content = f"// Generated {lang} module\n\nconsole.log('Hello, World!');\n"
        
        files.append(GeneratedFile(
            path=f"main{ext}",
            description="主程序文件",
            content=content
        ))
        
        return files
    
    def _generate_config_files(self, request: CodeGenerationRequest, architecture: Dict[str, Any]) -> List[GeneratedFile]:
        """生成配置文件"""
        files = []
        lang = request.language
        
        # .gitignore
        files.append(GeneratedFile(
            path=".gitignore",
            description="Git忽略文件",
            content='''# Generated by AI Code Generator
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.env
.venv
venv/
ENV/
.idea/
.vscode/
*.swp
*.swo
*~
.DS_Store
'''
        ))
        
        # .env.example
        files.append(GeneratedFile(
            path=".env.example",
            description="环境变量示例",
            content='''# Environment Configuration
# Copy this file to .env and fill in your values

DEBUG=true
LOG_LEVEL=info
'''
        ))
        
        return files
    
    def _generate_test_files(self, request: CodeGenerationRequest, architecture: Dict[str, Any]) -> List[GeneratedFile]:
        """生成测试文件"""
        files = []
        lang = request.language
        
        if lang == "python":
            files.append(GeneratedFile(
                path="test_main.py",
                description="测试文件",
                content='''#!/usr/bin/env python3
"""Tests - Generated by AI Code Generator"""

import pytest

def test_example():
    assert True

if __name__ == "__main__":
    pytest.main([__file__])
'''
            ))
        
        return files
    
    def _generate_doc_files(self, request: CodeGenerationRequest, architecture: Dict[str, Any]) -> List[GeneratedFile]:
        """生成文档文件"""
        files = []
        
        files.append(GeneratedFile(
            path="README.md",
            description="项目文档",
            content=f'''# Generated Project

Generated by AI Code Generator

## Description

{request.prompt}

## Setup

See setup instructions below.

## License

MIT
'''
        ))
        
        return files
    
    def _generate_dependencies(self, request: CodeGenerationRequest, architecture: Dict[str, Any]) -> List[str]:
        """生成依赖列表"""
        deps = []
        framework = architecture.get("framework")
        
        if framework and framework in self.FRAMEWORK_TEMPLATES:
            deps.extend(self.FRAMEWORK_TEMPLATES[framework]["dependencies"])
        
        return deps
    
    def _generate_setup_instructions(self, request: CodeGenerationRequest, architecture: Dict[str, Any]) -> List[str]:
        """生成设置说明"""
        instructions = []
        lang = request.language
        framework = architecture.get("framework")
        
        if lang == "python":
            instructions.extend([
                "1. Create virtual environment: python -m venv venv",
                "2. Activate: source venv/bin/activate (or venv\\Scripts\\activate on Windows)",
                "3. Install dependencies: pip install -r requirements.txt",
                "4. Copy .env.example to .env and configure",
                "5. Run: python main.py"
            ])
        elif lang in ["typescript", "javascript"]:
            instructions.extend([
                "1. Install dependencies: npm install",
                "2. Copy .env.example to .env and configure",
                "3. Run: npm start"
            ])
        
        return instructions
    
    def save_files(self, result: CodeGenerationResult, output_dir: Optional[str] = None) -> List[str]:
        """
        保存生成的文件到磁盘
        
        Args:
            result: 代码生成结果
            output_dir: 输出目录（默认使用request中的output_dir）
            
        Returns:
            保存的文件路径列表
        """
        output_dir = output_dir or result.request.output_dir
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        
        for file in result.files:
            file_path = output_path / file.path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(file.content, encoding='utf-8')
            saved_files.append(str(file_path))
        
        return saved_files


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Code Generator")
    parser.add_argument("prompt", help="Code generation prompt")
    parser.add_argument("--language", default="python", help="Target language")
    parser.add_argument("--framework", help="Target framework")
    parser.add_argument("--output", default="./generated", help="Output directory")
    parser.add_argument("--provider", default="claude", help="AI provider (claude/openai/kimi)")
    parser.add_argument("--no-tests", action="store_true", help="Skip test generation")
    parser.add_argument("--no-docs", action="store_true", help="Skip documentation")
    
    args = parser.parse_args()
    
    generator = AICodeGenerator(api_provider=args.provider)
    
    request = CodeGenerationRequest(
        prompt=args.prompt,
        language=args.language,
        framework=args.framework,
        output_dir=args.output,
        include_tests=not args.no_tests,
        include_docs=not args.no_docs
    )
    
    result = generator.generate(request)
    
    if result.success:
        print(f"✓ Generated {len(result.files)} files")
        print(f"  Method: {result.generation_method}")
        if result.api_provider:
            print(f"  Provider: {result.api_provider}")
        
        saved = generator.save_files(result)
        print(f"✓ Saved to: {args.output}")
        for f in saved:
            print(f"  - {f}")
    else:
        print(f"✗ Generation failed: {result.error}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
