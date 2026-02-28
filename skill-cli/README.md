# Skill CLI

技能包CLI执行器 - 将SKILL.md定义转化为可执行命令，支持AI自然语言交互

## 功能特性

- **命令解析**: 将自然语言命令映射到具体功能
- **参数处理**: 支持标准CLI参数格式
- **技能发现**: 自动扫描并注册技能包
- **AI桥接**: 自然语言到技能命令的智能转换
- **真实数据接入**: 已接入 finance-pro 真实数据源
- **上下文管理**: 支持多轮对话上下文保持
- **意图识别**: 基于关键词和模式的智能意图解析
- **技能路由**: 动态路由到对应的技能处理器

## 安装

```bash
chmod +x skill-cli
ln -s $(pwd)/skill-cli /usr/local/bin/skill-cli
```

## 快速开始

### 命令行模式

```bash
# 列出所有技能
skill-cli list

# 执行具体命令
skill-cli finance-pro quote --symbol 000001.SZ
skill-cli coding-pro generate --prompt "Python爬虫"
```

### AI桥接模式

```bash
# 自然语言命令
skill-bridge "分析一下茅台股票"
skill-bridge "生成一个Python爬虫"
```

## 详细使用指南

### 1. 技能列表与发现

```bash
# 查看所有可用技能
skill-cli list

# 查看特定技能详情
skill-cli info finance-pro
```

### 2. 金融数据查询

```bash
# 获取股票实时行情
skill-cli finance-pro quote --symbol 000001.SZ

# 获取技术指标
skill-cli finance-pro technical --symbol 000001.SZ --indicators MACD,KDJ

# 获取财务数据
skill-cli finance-pro financial --symbol 000001.SZ
```

### 3. 代码生成

```bash
# 生成Python代码
skill-cli coding-pro generate --prompt "创建一个HTTP服务器"

# 代码审查
skill-cli coding-pro review --file path/to/code.py

# 生成项目结构
skill-cli coding-pro repo --name myproject --type python
```

### 4. 产品分析

```bash
# 竞品分析
skill-cli product-pro analyze --product "产品名称"

# 用户画像
skill-cli product-pro persona --target "目标用户"
```

### 5. 研究助手

```bash
# 搜索信息
skill-cli research-pro search --query "AI最新进展"

# 生成报告
skill-cli research-pro report --topic "量子计算"
```

## 架构设计

### 核心组件

```
┌─────────────────────────────────────────────────────────────┐
│                        Skill CLI                             │
├─────────────┬─────────────┬─────────────┬───────────────────┤
│  Intent     │  Context    │  Executor   │  Data Adapter     │
│  Parser     │  Manager    │             │                   │
├─────────────┴─────────────┴─────────────┴───────────────────┤
│                      Skill Router                            │
├─────────────────────────────────────────────────────────────┤
│  Finance    │  Coding     │  Product    │  Research         │
│  Pro        │  Pro        │  Pro        │  Pro              │
└─────────────────────────────────────────────────────────────┘
```

### 数据流

1. **输入解析**: 用户输入 → 意图解析器 → 结构化命令
2. **路由分发**: 技能路由器 → 对应技能处理器
3. **数据获取**: 技能处理器 → 数据适配器 → 真实/Mock数据
4. **结果返回**: 格式化输出 → 用户界面

## 支持的技能

| 技能包 | 状态 | 数据类型 | 功能描述 |
|--------|------|----------|----------|
| finance-pro | ✅ | 真实数据 | 股票行情、技术指标、财务数据 |
| coding-pro | ✅ | mock | 代码生成、代码审查、项目模板 |
| product-pro | ✅ | mock | 竞品分析、用户画像、需求文档 |
| research-pro | ✅ | mock | 信息搜索、报告生成、数据分析 |
| stock-portfolio-analyzer | ✅ | 真实数据 | 股票组合分析、持仓建议 |

## 开发指南

### 添加新技能

1. 在 `SKILLS_DIR` 创建技能目录
2. 添加 `SKILL.md` 定义技能接口
3. 在 `skill-cli.py` 添加命令处理器
4. 注册到命令映射表

### 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_intent_parser.py -v
pytest tests/test_executor.py -v
pytest tests/test_skill_router.py -v

# 运行性能测试
pytest tests/test_performance.py -v
```

### 代码规范

- 遵循 PEP 8 代码风格
- 使用类型注解
- 添加 docstring 文档
- 保持单元测试覆盖率 > 80%

## 配置

### 环境变量

```bash
# 技能目录路径
export SKILLS_DIR=/path/to/skills

# 共享数据目录
export SHARED_DIR=/path/to/shared

# 调试模式
export SKILL_CLI_DEBUG=1
```

### 配置文件

```json
{
  "default_skill": "finance-pro",
  "timeout": 30,
  "max_retries": 3,
  "output_format": "json"
}
```

## 故障排除

### 常见问题

**Q: 技能包未找到**
```bash
# 检查技能目录
ls $SKILLS_DIR

# 确认 SKILL.md 存在
cat $SKILLS_DIR/skill-name/SKILL.md
```

**Q: 命令执行失败**
```bash
# 启用调试模式
export SKILL_CLI_DEBUG=1
skill-cli finance-pro quote --symbol 000001.SZ
```

**Q: 数据获取超时**
```bash
# 增加超时时间
export SKILL_CLI_TIMEOUT=60
```

## 项目结构

```
skill-cli/
├── skill-cli              # Bash入口脚本
├── skill-cli.py           # Python核心实现
├── ai_bridge.py           # AI桥接层
├── executor.py            # 执行引擎
├── data_adapter.py        # 数据适配器
├── intent_parser.py       # 意图解析器
├── context_manager.py     # 上下文管理器
├── skill_router.py        # 技能路由器
├── tests/                 # 测试目录
│   ├── test_cli_entry.py
│   ├── test_executor.py
│   ├── test_intent_parser.py
│   ├── test_natural_language.py
│   ├── test_performance.py
│   └── test_skill_router.py
├── README.md              # 项目文档
└── SKILL.md               # 技能定义文档
```

## 路线图

- [x] 基础CLI框架
- [x] 意图解析器
- [x] 技能路由器
- [x] AI桥接模式
- [x] 上下文管理
- [x] 真实数据接入 (finance-pro)
- [ ] 插件系统
- [ ] 配置热加载
- [ ] 交互式Shell

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交代码变更
4. 确保测试通过
5. 提交 Pull Request

## License

MIT

## 联系方式

- 项目主页: https://github.com/claw-bft/ai-agent-lab
- 问题反馈: https://github.com/claw-bft/ai-agent-lab/issues
