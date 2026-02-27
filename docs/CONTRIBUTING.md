# 🤝 贡献指南

感谢您对 AI Agent Lab 的兴趣！本指南将帮助您快速成为项目贡献者。

---

## 📋 目录

- [快速开始](#快速开始)
- [贡献类型](#贡献类型)
- [开发环境](#开发环境)
- [提交规范](#提交规范)
- [代码审查](#代码审查)
- [技能包开发](#技能包开发)
- [常见问题](#常见问题)

---

## 🚀 快速开始

### 1. Fork 仓库

```bash
# 访问 https://github.com/claw-bft/ai-agent-lab
# 点击右上角的 "Fork" 按钮
```

### 2. 克隆您的 Fork

```bash
git clone https://github.com/YOUR_USERNAME/ai-agent-lab.git
cd ai-agent-lab
```

### 3. 添加上游仓库

```bash
git remote add upstream https://github.com/claw-bft/ai-agent-lab.git
```

### 4. 创建分支

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

---

## 🎯 贡献类型

### 我们欢迎以下贡献：

| 类型 | 描述 | 示例 |
|------|------|------|
| 🐛 Bug 修复 | 修复代码中的问题 | 修复测试警告、修复数据解析错误 |
| ✨ 新功能 | 添加新功能或改进 | 新增技能包、添加新命令 |
| 📚 文档 | 改进或添加文档 | 更新 SKILL.md、添加使用示例 |
| 🧪 测试 | 添加或改进测试 | 提高测试覆盖率、添加边界测试 |
| ⚡ 性能 | 性能优化 | 优化查询速度、减少内存使用 |
| 🔧 工具 | 开发工具改进 | 改进 CLI、添加调试工具 |

---

## 🛠️ 开发环境

### 系统要求

- Python 3.10+
- Git
- (可选) Node.js 16+ (用于 ClawHub 前端)

### 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定模块
pytest finance-pro/tests/

# 生成覆盖率报告
pytest --cov=. --cov-report=html

# 运行特定测试
pytest -k test_quote
```

### 代码检查

```bash
# 运行代码格式化
black .

# 运行代码检查
flake8

# 运行类型检查
mypy
```

---

## 📝 提交规范

### Commit Message 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

| 类型 | 描述 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `style` | 代码格式（不影响功能） |
| `refactor` | 代码重构 |
| `test` | 测试相关 |
| `chore` | 构建/工具相关 |

### 示例

```bash
# 新功能
feat(finance-pro): 添加加密货币实时行情支持

# Bug 修复
fix(skill-cli): 修复自然语言解析中的空指针异常

# 文档
docs: 更新 README 中的安装说明

# 测试
test(memory-enhanced): 添加向量搜索边界测试
```

---

## 🔍 代码审查

### 提交 PR 前检查清单

- [ ] 代码可以正常运行
- [ ] 添加了必要的测试
- [ ] 所有测试通过
- [ ] 代码符合项目风格
- [ ] 更新了相关文档
- [ ] Commit message 符合规范

### PR 流程

1. **创建 PR**: 从您的分支向 `main` 分支创建 Pull Request
2. **填写模板**: 使用 PR 模板填写相关信息
3. **等待审查**: 维护者会在 48 小时内审查
4. **处理反馈**: 根据审查意见修改代码
5. **合并**: 审查通过后会被合并

---

## 📦 技能包开发

### 技能包结构

每个技能包应遵循以下结构：

```
your-skill/
├── SKILL.md              # 技能文档（必需）
├── __init__.py           # 入口点
├── core.py               # 核心逻辑
├── config.py             # 配置管理
├── tests/                # 测试目录
│   ├── __init__.py
│   ├── test_core.py
│   └── fixtures/         # 测试数据
├── examples/             # 使用示例
└── requirements.txt      # 依赖（如有）
```

### SKILL.md 模板

```markdown
---
name: your-skill
description: 简短描述技能功能
version: 1.0.0
author: Your Name
tags: [tag1, tag2]
---

# Your Skill

## 功能概述

简要描述技能的功能和价值。

## 安装

```bash
claw install your-skill
```

## 使用方法

### 命令行

```bash
your-skill command --option value
```

### Python API

```python
from your_skill import YourSkill

skill = YourSkill()
result = skill.do_something()
```

## 配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| API_KEY | str | - | API 密钥 |
| TIMEOUT | int | 30 | 超时时间 |

## 示例

```python
# 示例代码
```

## 依赖

- python >= 3.10
- requests >= 2.28.0

## 更新日志

### v1.0.0
- 初始版本
```

### 测试要求

- 每个功能至少一个测试
- 测试覆盖率目标 80%+
- 包含边界情况测试
- 使用 pytest 框架

### 示例测试

```python
import pytest
from your_skill.core import YourSkill

class TestYourSkill:
    def test_basic_functionality(self):
        skill = YourSkill()
        result = skill.process("input")
        assert result is not None
        assert "expected_key" in result
    
    def test_edge_cases(self):
        skill = YourSkill()
        # 测试空输入
        with pytest.raises(ValueError):
            skill.process("")
```

---

## ❓ 常见问题

### Q: 如何报告 Bug？

A: 使用 GitHub Issues 模板，包含：
- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（Python 版本、操作系统）

### Q: 可以贡献什么类型的技能包？

A: 任何有价值的技能！例如：
- 数据分析工具
- API 集成
- 自动化脚本
- 内容生成
- 实用工具

### Q: 代码风格要求？

A: 我们使用：
- **Black** 进行代码格式化
- **Flake8** 进行代码检查
- **Google Style** 文档字符串

### Q: 如何成为维护者？

A: 持续贡献高质量 PR，积极参与代码审查和社区讨论。维护者团队会主动邀请。

---

## 📞 获取帮助

- 💬 [Discord 社区](https://discord.gg/clawd)
- 🐛 [GitHub Issues](https://github.com/claw-bft/ai-agent-lab/issues)
- 📧 邮件: contact@clawhub.com

---

## 🏆 贡献者

感谢所有为 AI Agent Lab 做出贡献的人！

<a href="https://github.com/claw-bft/ai-agent-lab/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=claw-bft/ai-agent-lab" />
</a>

---

## 📄 许可证

通过贡献代码，您同意您的贡献将在 [MIT License](./LICENSE) 下发布。

---

<p align="center">
  <i>Happy Coding! 🚀</i>
</p>
