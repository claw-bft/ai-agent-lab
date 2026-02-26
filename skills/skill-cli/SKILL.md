---
name: skill-cli
description: 技能包CLI执行器 - 将SKILL.md定义转化为可执行命令
---

# Skill CLI 执行器

统一入口，让4个专业技能包(finance/coding/product/research-pro)真正可执行。

## 功能

- **命令解析**: 将自然语言命令映射到具体功能
- **参数处理**: 支持标准CLI参数格式
- **技能发现**: 自动扫描并注册技能包
- **JSON输出**: 支持程序化调用

## 安装

```bash
# 添加到PATH
chmod +x /root/.openclaw/workspace/skills/skill-cli/skill-cli
ln -s /root/.openclaw/workspace/skills/skill-cli/skill-cli /usr/local/bin/skill-cli
```

## 使用

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

## 支持的技能

| 技能包 | 状态 | 命令示例 |
|--------|------|----------|
| coding-pro | ✅ 已实现 | generate, review, repo, cicd |
| finance-pro | ✅ 已实现 | quote, analyze, financial, alert |
| product-pro | ✅ 已实现 | competitor, prd, ppt, research |
| research-pro | ✅ 已实现 | deep, analyze, search, monitor |

## 架构

```
skill-cli/
├── skill-cli          # Bash入口脚本
├── skill-cli.py       # Python核心实现
└── SKILL.md           # 本文档
```

## 扩展新技能

1. 在 `build_command_map()` 中添加技能名和处理器映射
2. 实现具体的处理器函数
3. 更新 SKILL.md 文档

## 技术债务

- [ ] 自然语言命令需要接入AI执行
- [ ] 缺少真正的数据获取实现(股票/搜索等)
- [ ] 需要添加配置管理和凭证安全存储
