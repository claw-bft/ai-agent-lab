---
name: skill-cli
description: 技能包CLI执行器 - 将SKILL.md定义转化为可执行命令，支持AI自然语言交互
---

# Skill CLI 执行器

统一入口，让4个专业技能包(finance/coding/product/research-pro)真正可执行，支持自然语言和命令行两种交互方式。

## 功能

- **命令解析**: 将自然语言命令映射到具体功能
- **参数处理**: 支持标准CLI参数格式
- **技能发现**: 自动扫描并注册技能包
- **JSON输出**: 支持程序化调用
- **AI桥接**: 自然语言到技能命令的智能转换

## 安装

```bash
# 添加到PATH
chmod +x /root/.openclaw/workspace/skills/skill-cli/skill-cli
chmod +x /root/.openclaw/workspace/skills/skill-cli/ai_bridge.py
ln -s /root/.openclaw/workspace/skills/skill-cli/skill-cli /usr/local/bin/skill-cli
ln -s /root/.openclaw/workspace/skills/skill-cli/ai_bridge.py /usr/local/bin/skill-bridge
```

## 使用方式

### 方式1: 命令行模式 (skill-cli)

```bash
# 列出所有技能
skill-cli list

# 查看技能帮助
skill-cli coding-pro help
skill-cli finance-pro help

# 执行具体命令
skill-cli finance-pro quote --symbol 000001.SZ
skill-cli research-pro deep --topic "AI发展趋势"
skill-cli product-pro competitor --product "AI代码助手"
```

### 方式2: AI桥接模式 (skill-bridge) ⭐推荐

```bash
# 直接输入自然语言命令
skill-bridge "分析一下茅台股票"
skill-bridge "生成一个Python爬虫"
skill-bridge "深度研究AI发展趋势"
skill-bridge "分析AI代码助手竞品"

# 交互模式
skill-bridge --interactive

# 查看可用技能
skill-bridge --skills

# 查看技能帮助
skill-bridge --help-skill finance-pro
```

### 方式3: Python API调用

```python
from ai_bridge import execute_skill, quick_quote, quick_research

# 执行自然语言命令
result = execute_skill("分析一下茅台股票")
print(result)

# 快捷函数
quote = quick_quote("600519.SH")
research = quick_research("AI发展趋势")
```

## 支持的技能

| 技能包 | 状态 | 自然语言示例 | 命令行示例 |
|--------|------|--------------|------------|
| finance-pro | ✅ 已实现 | "分析一下茅台股票" | `finance-pro quote --symbol 600519.SH` |
| coding-pro | ✅ 已实现 | "生成一个Python爬虫" | `coding-pro generate --prompt "Python爬虫"` |
| product-pro | ✅ 已实现 | "分析AI代码助手竞品" | `product-pro competitor --product "AI助手"` |
| research-pro | ✅ 已实现 | "深度研究AI发展趋势" | `research-pro deep --topic "AI趋势"` |

## 架构

```
skill-cli/
├── skill-cli          # Bash入口脚本
├── skill-cli.py       # Python核心实现
├── ai_bridge.py       # AI桥接层 ⭐新增
├── executor.py        # 执行引擎
└── SKILL.md           # 本文档
```

### AI桥接层 (ai_bridge.py)

核心组件：
- **AIBridge**: 主桥接类，处理自然语言输入
- **IntentParser**: 意图解析器，识别技能和动作
- **SkillRouter**: 技能路由器，分发到对应处理器
- **ContextManager**: 上下文管理，支持多轮对话

## 扩展新技能

1. 在 `executor.py` 的 `SkillRouter._register_handlers()` 中添加处理器
2. 实现对应的 `SkillHandler` 子类
3. 在 `ai_bridge.py` 的 `_preprocess_input()` 中添加意图映射
4. 更新 SKILL.md 文档

## 技术债务

- [x] 自然语言命令接入AI执行 ✅ 已完成
- [ ] 真正的数据获取实现(股票/搜索等) - 当前使用mock数据
- [ ] 添加配置管理和凭证安全存储
- [ ] 添加测试覆盖率

## 更新日志

### 2026-02-27
- ✅ 实现AI桥接层 (ai_bridge.py)
- ✅ 支持自然语言到技能命令的转换
- ✅ 添加mock数据模式用于测试
- ✅ 统一执行结果格式
- ✅ 支持交互模式和API调用
