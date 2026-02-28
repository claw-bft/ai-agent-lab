# Coding Pro

程序员专业技能包 - 智能编码、版本协作、DevOps自动化

## 功能特性

### 1. 智能代码开发 (AI Coding)
- 自然语言代码生成，支持20+编程语言
- 智能错误定位与调试
- 性能瓶颈识别与优化建议
- 代码重构建议

### 2. AI代码生成器
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

### 3. 版本控制与协作
- Git仓库全功能管理
- 智能分支策略优化
- 代码冲突自动解决
- 自动化代码审查

### 4. DevOps自动化
- CI/CD流水线自然语言配置
- 多平台支持 (Jenkins/GitLab CI/GitHub Actions)
- 基础设施即代码 (Terraform/Pulumi)
- 数据库Schema版本管理

## 安装

```bash
# 克隆仓库
git clone <repository-url>
cd coding-pro

# 安装依赖 (可选，用于AI代码生成)
pip install anthropic  # 用于Claude API
pip install openai     # 用于OpenAI/Kimi API
```

## 快速开始

### AI代码生成

```bash
# 使用Claude生成FastAPI项目 (默认)
python ai_code_generator.py "创建一个用户管理API服务" --language python --framework fastapi --output ./user-api

# 使用OpenAI生成
python ai_code_generator.py "创建一个文件批量重命名工具" --language python --provider openai --output ./rename-tool

# 使用Kimi生成
python ai_code_generator.py "创建一个待办事项Web应用" --language typescript --framework react --provider kimi --output ./todo-app
```

### Python API使用

```python
from ai_code_generator import AICodeGenerator, CodeGenerationRequest

# 使用Claude (默认)
generator = AICodeGenerator(api_provider="claude")

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

## 环境变量配置

```bash
# Claude (推荐)
export ANTHROPIC_API_KEY="your-api-key"

# 或 OpenAI
export OPENAI_API_KEY="your-api-key"

# 或 Kimi
export KIMI_API_KEY="your-api-key"
```

## 文件结构

```
coding-pro/
├── README.md                  # 本文件
├── SKILL.md                   # 技能包详细文档
├── coding-pro.py             # 基础代码生成工具
├── ai_code_generator.py      # AI代码生成器
├── demo_generator.py         # 演示生成器
├── tests/                    # 测试套件
└── generated_examples/       # 生成的示例项目
```

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_ai_code_generator.py -v

# 生成覆盖率报告
pytest tests/ --cov=. --cov-report=html
```

## 依赖工具

- Python 3.8+
- git
- github-cli (gh)
- docker (可选)
- kubectl (可选)
- terraform (可选)

## 贡献

欢迎提交Issue和Pull Request。

## 许可证

MIT License
