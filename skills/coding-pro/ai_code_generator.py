#!/usr/bin/env python3
"""
AI Code Generator - 智能代码生成模块
集成Claude API实现自然语言到代码的转换
"""

import os
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class CodeGenerationRequest:
    """代码生成请求"""
    prompt: str
    language: str = "python"
    framework: Optional[str] = None
    output_dir: str = "./generated"
    include_tests: bool = True
    include_docs: bool = True


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
    error: Optional[str] = None


class AICodeGenerator:
    """AI代码生成器"""
    
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
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
    
    def generate(self, request: CodeGenerationRequest) -> CodeGenerationResult:
        """
        根据请求生成代码
        
        这是一个模拟实现，实际应该调用Claude API
        这里使用模板和规则生成合理的代码结构
        """
        try:
            # 分析需求
            architecture = self._analyze_requirements(request)
            
            # 生成文件
            files = self._generate_files(request, architecture)
            
            # 生成依赖列表
            dependencies = self._generate_dependencies(request, architecture)
            
            # 生成安装说明
            setup_instructions = self._generate_setup_instructions(request, architecture)
            
            return CodeGenerationResult(
                success=True,
                request=request,
                files=files,
                architecture=architecture,
                dependencies=dependencies,
                setup_instructions=setup_instructions
            )
            
        except Exception as e:
            return CodeGenerationResult(
                success=False,
                request=request,
                files=[],
                architecture={},
                dependencies=[],
                setup_instructions=[],
                error=str(e)
            )
    
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
        """生成项目文件"""
        files = []
        lang = request.language
        framework = architecture.get("framework")
        project_type = architecture.get("project_type")
        
        # 根据项目类型生成文件
        if project_type == "api":
            files.extend(self._generate_api_files(request, architecture))
        elif project_type == "cli":
            files.extend(self._generate_cli_files(request, architecture))
        elif project_type == "web":
            files.extend(self._generate_web_files(request, architecture))
        else:
            files.extend(self._generate_generic_files(request, architecture))
        
        # 添加配置文件
        files.extend(self._generate_config_files(request, architecture))
        
        # 添加测试文件
        if request.include_tests:
            files.extend(self._generate_test_files(request, architecture))
        
        # 添加文档
        if request.include_docs:
            files.extend(self._generate_doc_files(request, architecture))
        
        return files
    
    def _generate_api_files(self, request: CodeGenerationRequest, architecture: Dict[str, Any]) -> List[GeneratedFile]:
        """生成API项目文件"""
        files = []
        lang = request.language
        framework = architecture.get("framework")
        
        if lang == "python" and framework == "fastapi":
            # main.py
            files.append(GeneratedFile(
                path="main.py",
                description="FastAPI应用入口",
                content='''#!/usr/bin/env python3
"""
FastAPI Application
Generated by AI Code Generator
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

app = FastAPI(
    title="API Service",
    description="Auto-generated API service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

# In-memory storage (replace with database in production)
items_db = []
item_id_counter = 1

# Routes
@app.get("/")
def read_root():
    return {"message": "Welcome to API Service", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/items", response_model=List[Item])
def list_items():
    return items_db

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    item = next((i for i in items_db if i["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.post("/items", response_model=Item)
def create_item(item: ItemCreate):
    global item_id_counter
    new_item = {
        "id": item_id_counter,
        "name": item.name,
        "description": item.description,
        "price": item.price
    }
    items_db.append(new_item)
    item_id_counter += 1
    return new_item

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: ItemCreate):
    existing = next((i for i in items_db if i["id"] == item_id), None)
    if not existing:
        raise HTTPException(status_code=404, detail="Item not found")
    existing["name"] = item.name
    existing["description"] = item.description
    existing["price"] = item.price
    return existing

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    global items_db
    item = next((i for i in items_db if i["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    items_db = [i for i in items_db if i["id"] != item_id]
    return {"message": "Item deleted"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
            ))
            
            # models.py
            files.append(GeneratedFile(
                path="models.py",
                description="数据模型定义",
                content='''"""
Data Models
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = True
    message: Optional[str] = None

class ErrorResponse(BaseResponse):
    """错误响应模型"""
    success: bool = False
    error_code: Optional[str] = None

class PaginatedResponse(BaseModel):
    """分页响应模型"""
    total: int
    page: int
    page_size: int
    items: List[dict]
'''
            ))
            
            # config.py
            files.append(GeneratedFile(
                path="config.py",
                description="应用配置",
                content='''"""
Application Configuration
"""

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用设置"""
    app_name: str = "API Service"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "sqlite:///./app.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
'''
            ))
            
            # requirements.txt
            files.append(GeneratedFile(
                path="requirements.txt",
                description="Python依赖",
                content='''fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-multipart>=0.0.6
'''
            ))
            
            # Dockerfile
            files.append(GeneratedFile(
                path="Dockerfile",
                description="Docker镜像配置",
                content='''FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "main.py"]
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
"""
CLI Tool
Generated by AI Code Generator
"""

import argparse
import sys
from typing import Optional

__version__ = "1.0.0"

def main():
    parser = argparse.ArgumentParser(
        prog="cli-tool",
        description="A powerful CLI tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s hello --name World
  %(prog)s --version
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Hello command
    hello_parser = subparsers.add_parser("hello", help="Say hello")
    hello_parser.add_argument("--name", default="World", help="Name to greet")
    hello_parser.add_argument("--upper", action="store_true", help="Uppercase output")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configuration commands")
    config_parser.add_argument("--show", action="store_true", help="Show current config")
    
    args = parser.parse_args()
    
    if args.command == "hello":
        message = f"Hello, {args.name}!"
        if args.upper:
            message = message.upper()
        print(message)
    elif args.command == "config":
        if args.show:
            print("Current configuration:")
            print("  Version:", __version__)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
            ))
            
            files.append(GeneratedFile(
                path="setup.py",
                description="包安装配置",
                content='''from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cli-tool",
    version="1.0.0",
    author="Generated by AI",
    description="A powerful CLI tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "cli-tool=cli:main",
        ],
    },
)
'''
            ))
            
            files.append(GeneratedFile(
                path="requirements.txt",
                description="Python依赖",
                content='''# CLI dependencies
# Add your dependencies here
'''
            ))
        
        return files
    
    def _generate_web_files(self, request: CodeGenerationRequest, architecture: Dict[str, Any]) -> List[GeneratedFile]:
        """生成Web项目文件"""
        files = []
        lang = request.language
        
        if lang in ["typescript", "javascript"]:
            files.append(GeneratedFile(
                path="index.html",
                description="HTML入口",
                content='''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Application</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div id="app">
        <header>
            <h1>Welcome</h1>
        </header>
        <main>
            <p>Generated by AI Code Generator</p>
        </main>
    </div>
    <script src="app.js"></script>
</body>
</html>
'''
            ))
            
            files.append(GeneratedFile(
                path="style.css",
                description="样式文件",
                content='''/* Global styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    background: #f5f5f5;
}

#app {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    background: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

main {
    background: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
'''
            ))
            
            files.append(GeneratedFile(
                path="app.js",
                description="JavaScript入口",
                content='''// Application entry point
console.log('Application loaded');

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM ready');
    
    // Initialize application
    initApp();
});

function initApp() {
    console.log('Initializing application...');
    // Add your initialization code here
}
'''
            ))
            
            files.append(GeneratedFile(
                path="package.json",
                description="Node.js包配置",
                content='''{
  "name": "web-app",
  "version": "1.0.0",
  "description": "Generated web application",
  "main": "app.js",
  "scripts": {
    "start": "node app.js",
    "dev": "node app.js",
    "build": "echo 'Build script not configured'",
    "test": "echo 'Test script not configured'"
  },
  "keywords": [],
  "author": "Generated by AI",
  "license": "MIT",
  "dependencies": {},
  "devDependencies": {}
}
'''
            ))
        
        return files
    
    def _generate_generic_files(self, request: CodeGenerationRequest, architecture: Dict[str, Any]) -> List[GeneratedFile]:
        """生成通用项目文件"""
        files = []
        lang = request.language
        ext = self.LANGUAGE_TEMPLATES.get(lang, {}).get("extension", ".py")
        
        files.append(GeneratedFile(
            path=f"main{ext}",
            description="主程序文件",
            content=f'''#!/usr/bin/env python3
"""
{request.prompt}
Generated by AI Code Generator
"""

def main():
    """主函数"""
    print("Hello from generated project!")
    print(f"Prompt: {request.prompt}")
    
    # TODO: Implement your logic here
    pass

if __name__ == "__main__":
    main()
'''
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
            content='''# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Build outputs
dist/
build/
*.egg-info/

# Environment variables
.env
.env.local
.env.*.local
'''
        ))
        
        # .env.example
        files.append(GeneratedFile(
            path=".env.example",
            description="环境变量示例",
            content='''# Application settings
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./app.db

# Security
SECRET_KEY=your-secret-key-here
'''
        ))
        
        return files
    
    def _generate_test_files(self, request: CodeGenerationRequest, architecture: Dict[str, Any]) -> List[GeneratedFile]:
        """生成测试文件"""
        files = []
        lang = request.language
        
        if lang == "python":
            files.append(GeneratedFile(
                path="tests/test_main.py",
                description="主测试文件",
                content='''"""
Tests for main module
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_import():
    """Test that main module can be imported"""
    try:
        import main
        assert True
    except ImportError:
        assert False, "Failed to import main module"

def test_placeholder():
    """Placeholder test"""
    assert True
'''
            ))
            
            files.append(GeneratedFile(
                path="tests/__init__.py",
                description="测试包初始化",
                content='''# Tests package
'''
            ))
            
            files.append(GeneratedFile(
                path="pytest.ini",
                description="pytest配置",
                content='''[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
'''
            ))
        
        return files
    
    def _generate_doc_files(self, request: CodeGenerationRequest, architecture: Dict[str, Any]) -> List[GeneratedFile]:
        """生成文档文件"""
        files = []
        
        # README.md
        files.append(GeneratedFile(
            path="README.md",
            description="项目说明文档",
            content=f'''# Generated Project

{request.prompt}

## Features

- Auto-generated project structure
- Clean, modular code organization
- Ready for development

## Project Type

- **Language**: {request.language}
- **Framework**: {architecture.get("framework", "None")}
- **Type**: {architecture.get("project_type", "generic")}
- **Complexity**: {architecture.get("complexity", "low")}

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd <project-directory>

# Install dependencies
{self._get_install_command(request.language)}
```

## Usage

```bash
# Run the application
{self._get_run_command(request.language, architecture)}
```

## Development

```bash
# Run tests
{self._get_test_command(request.language)}
```

## Project Structure

```
.
├── main.*          # Application entry point
├── config.*        # Configuration
├── tests/          # Test files
├── .gitignore      # Git ignore rules
└── README.md       # This file
```

## License

MIT License
'''
        ))
        
        return files
    
    def _generate_dependencies(self, request: CodeGenerationRequest, architecture: Dict[str, Any]) -> List[str]:
        """生成依赖列表"""
        deps = []
        lang = request.language
        framework = architecture.get("framework")
        features = architecture.get("features", [])
        
        if lang == "python":
            if framework == "fastapi":
                deps.extend(["fastapi>=0.104.0", "uvicorn[standard]>=0.24.0", "pydantic>=2.5.0"])
            elif framework == "flask":
                deps.extend(["flask>=3.0.0", "flask-sqlalchemy>=3.1.0"])
            elif framework == "django":
                deps.extend(["django>=5.0", "djangorestframework>=3.14.0"])
            
            if "database" in features:
                deps.append("sqlalchemy>=2.0.0")
            if "cache" in features:
                deps.append("redis>=5.0.0")
            if "auth" in features:
                deps.extend(["python-jose[cryptography]>=3.3.0", "passlib[bcrypt]>=1.7.4"])
            if "testing" in features or request.include_tests:
                deps.append("pytest>=7.4.0")
        
        elif lang in ["typescript", "javascript"]:
            if framework == "express":
                deps.extend(["express", "cors", "dotenv"])
            elif framework == "react":
                deps.extend(["react", "react-dom"])
        
        return deps
    
    def _generate_setup_instructions(self, request: CodeGenerationRequest, architecture: Dict[str, Any]) -> List[str]:
        """生成安装说明"""
        instructions = []
        lang = request.language
        
        instructions.append("1. Clone the repository")
        instructions.append(f"2. Install dependencies: {self._get_install_command(lang)}")
        instructions.append(f"3. Run the application: {self._get_run_command(lang, architecture)}")
        
        if request.include_tests:
            instructions.append(f"4. Run tests: {self._get_test_command(lang)}")
        
        return instructions
    
    def _get_install_command(self, language: str) -> str:
        """获取安装命令"""
        if language == "python":
            return "pip install -r requirements.txt"
        elif language in ["typescript", "javascript"]:
            return "npm install"
        elif language == "go":
            return "go mod tidy"
        elif language == "rust":
            return "cargo build"
        return "# Install dependencies"
    
    def _get_run_command(self, language: str, architecture: Dict[str, Any]) -> str:
        """获取运行命令"""
        if language == "python":
            return "python main.py"
        elif language in ["typescript", "javascript"]:
            return "npm start"
        elif language == "go":
            return "go run main.go"
        elif language == "rust":
            return "cargo run"
        return "# Run the application"
    
    def _get_test_command(self, language: str) -> str:
        """获取测试命令"""
        if language == "python":
            return "pytest"
        elif language in ["typescript", "javascript"]:
            return "npm test"
        elif language == "go":
            return "go test ./..."
        elif language == "rust":
            return "cargo test"
        return "# Run tests"


def main():
    """CLI入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Code Generator")
    parser.add_argument("prompt", help="Code generation prompt")
    parser.add_argument("--language", default="python", help="Programming language")
    parser.add_argument("--framework", help="Framework to use")
    parser.add_argument("--output", default="./generated", help="Output directory")
    parser.add_argument("--no-tests", action="store_true", help="Skip test generation")
    parser.add_argument("--no-docs", action="store_true", help="Skip documentation")
    
    args = parser.parse_args()
    
    request = CodeGenerationRequest(
        prompt=args.prompt,
        language=args.language,
        framework=args.framework,
        output_dir=args.output,
        include_tests=not args.no_tests,
        include_docs=not args.no_docs
    )
    
    generator = AICodeGenerator()
    result = generator.generate(request)
    
    if result.success:
        print(f"✓ Generated {len(result.files)} files")
        print(f"  Language: {result.architecture['language']}")
        print(f"  Framework: {result.architecture.get('framework', 'None')}")
        print(f"  Type: {result.architecture['project_type']}")
        print(f"  Complexity: {result.architecture['complexity']}")
        print(f"\nFiles:")
        for f in result.files:
            print(f"  - {f.path}: {f.description}")
    else:
        print(f"✗ Error: {result.error}")


if __name__ == "__main__":
    main()
