---
name: coding-pro
description: 程序员专业技能包 - 智能编码、版本协作、DevOps自动化
version: 1.1.0
---

# Coding Pro 技能包

## 功能模块

### 1. 智能代码开发 (AI Coding)
- 自然语言代码生成，支持20+编程语言
- 智能错误定位与调试
- 性能瓶颈识别与优化建议
- 代码重构建议

### 2. AI代码生成器 (ai_code_generator.py)
智能代码生成模块，支持根据自然语言描述自动生成完整项目结构。

**支持的语言：**
- Python (FastAPI, Flask, Django)
- TypeScript / JavaScript (Express, React)
- Go
- Rust

**AI模型支持：**
- **Claude** (默认) - 需要 `ANTHROPIC_API_KEY`
- **OpenAI** - 需要 `OPENAI_API_KEY`
- **Kimi** - 需要 `KIMI_API_KEY`

**功能特性：**
- 自动推断项目类型 (API/CLI/Web/Automation)
- 智能框架选择
- 自动生成配置文件 (.gitignore, .env.example)
- 自动生成测试文件
- 自动生成README文档
- 依赖管理
- **AI API错误自动重试** (最多3次，指数退避)
- **智能回退** (API不可用时使用模板生成)

**环境变量配置：**
```bash
# Claude (推荐)
export ANTHROPIC_API_KEY="your-api-key"

# 或 OpenAI
export OPENAI_API_KEY="your-api-key"

# 或 Kimi
export KIMI_API_KEY="your-api-key"
```

**使用示例：**
```bash
# 使用Claude生成FastAPI项目 (默认)
python ai_code_generator.py "创建一个用户管理API服务，包含CRUD操作" --language python --framework fastapi --output ./user-api

# 使用OpenAI生成
python ai_code_generator.py "创建一个文件批量重命名工具" --language python --provider openai --output ./rename-tool

# 使用Kimi生成
python ai_code_generator.py "创建一个待办事项Web应用" --language typescript --framework react --provider kimi --output ./todo-app

# 跳过测试和文档
python ai_code_generator.py "创建一个简单脚本" --no-tests --no-docs
```

**Python API使用：**
```python
from ai_code_generator import AICodeGenerator, CodeGenerationRequest

# 使用Claude (默认)
generator = AICodeGenerator(api_provider="claude")

# 或使用其他提供商
generator = AICodeGenerator(api_provider="openai")
# generator = AICodeGenerator(api_provider="kimi")

request = CodeGenerationRequest(
    prompt="创建一个用户认证API服务",
    language="python",
    framework="fastapi",
    output_dir="./auth-service",
    include_tests=True,
    include_docs=True
)

result = generator.generate(request)
if result.success:
    for file in result.files:
        print(f"Generated: {file.path}")
```

### 3. 版本控制与协作 (Version Control)
- Git仓库全功能管理
- 智能分支策略优化
- 代码冲突自动解决
- 自动化代码审查

### 4. DevOps自动化
- CI/CD流水线自然语言配置
- 多平台支持 (Jenkins/GitLab CI/GitHub Actions)
- 基础设施即代码 (Terraform/Pulumi)
- 数据库Schema版本管理

## 文件结构

```
skills/coding-pro/
├── SKILL.md                    # 本文件
├── coding-pro.py              # 基础代码生成工具
└── ai_code_generator.py       # AI代码生成器 (支持Claude/OpenAI/Kimi API)
```

## 依赖工具
- git
- github-cli (gh)
- docker
- kubectl
- terraform
- Python 3.8+
- anthropic (可选，用于Claude API)
- openai (可选，用于OpenAI/Kimi API)

## 使用示例

```bash
# 代码生成 (AI增强版 - 支持Claude/OpenAI/Kimi)
python ai_code_generator.py "创建一个Python FastAPI用户认证服务" --language python --framework fastapi

# 使用特定AI提供商
python ai_code_generator.py "创建一个React组件库" --language typescript --framework react --provider openai

# 代码审查
coding-pro review --path ./src --rules security,performance

# 创建GitHub仓库并推送
coding-pro repo create --name my-project --private --push

# 配置CI/CD流水线
coding-pro cicd setup --template python --provider github-actions

# 数据库迁移
coding-pro db migrate --direction up --env production
```

## 更新日志

### v1.2.0 (2026-02-27)
- AI代码生成器接入真实AI模型API (Claude/OpenAI/Kimi)
- 支持API错误处理和重试机制
- 智能回退到模板生成（当API不可用时）
- 新增 `--provider` 参数选择AI提供商

### v1.1.0 (2026-02-26)
- 新增 AI代码生成器 (ai_code_generator.py)
- 支持5种编程语言
- 支持智能项目类型推断
- 自动生成测试和文档

### v1.0.0
- 基础代码生成工具
- 代码审查功能
- CI/CD配置生成
