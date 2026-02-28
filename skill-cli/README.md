# Skill CLI

技能包CLI执行器 - 将SKILL.md定义转化为可执行命令，支持AI自然语言交互

## 功能特性

- **命令解析**: 将自然语言命令映射到具体功能
- **参数处理**: 支持标准CLI参数格式
- **技能发现**: 自动扫描并注册技能包
- **AI桥接**: 自然语言到技能命令的智能转换
- **真实数据接入**: 已接入 finance-pro 真实数据源

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

## 支持的技能

| 技能包 | 状态 | 数据类型 |
|--------|------|----------|
| finance-pro | ✅ | 真实数据 |
| coding-pro | ✅ | mock |
| product-pro | ✅ | mock |
| research-pro | ✅ | mock |

## 项目结构

```
skill-cli/
├── skill-cli          # Bash入口脚本
├── skill-cli.py       # Python核心实现
├── ai_bridge.py       # AI桥接层
├── executor.py        # 执行引擎
├── data_adapter.py    # 数据适配器
├── tests/            # 测试目录
└── SKILL.md          # 技能文档
```

## 测试

```bash
pytest tests/ -v
```

## License

MIT
