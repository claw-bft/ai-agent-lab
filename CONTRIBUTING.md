# Contributing to AI Agent Lab

感谢您对 AI Agent Lab 的兴趣！我们欢迎各种形式的贡献。

## 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议，请通过 GitHub Issues 提交：

1. 检查是否已有类似 issue
2. 使用对应的 issue 模板
3. 提供尽可能详细的信息

### 提交代码

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/claw-bft/ai-agent-lab.git
cd ai-agent-lab

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 运行测试
pytest
```

### 代码规范

- 遵循 PEP 8 规范
- 使用 Black 进行代码格式化
- 所有新功能必须包含测试
- 更新相关文档

### 提交信息规范

我们使用约定式提交 (Conventional Commits)：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `test:` 测试相关
- `refactor:` 代码重构
- `perf:` 性能优化
- `chore:` 构建/工具相关

示例：
```
feat(skill-cli): 添加自然语言命令解析器

支持从自然语言描述中提取意图和参数
```

## 技能包开发指南

### 创建新技能

1. 在 `skills/` 目录下创建新文件夹
2. 创建 `SKILL.md` 文档
3. 实现核心功能模块
4. 添加测试文件
5. 更新主 README

### 技能结构

```
skills/your-skill/
├── SKILL.md              # 技能文档
├── your_skill.py         # 主模块
├── tests/                # 测试目录
│   ├── __init__.py
│   └── test_your_skill.py
└── requirements.txt      # 依赖（可选）
```

## 行为准则

- 尊重所有参与者
- 接受建设性批评
- 关注对社区最有利的事情
- 展现同理心

## 许可证

通过贡献代码，您同意您的贡献将在 MIT 许可证下发布。
