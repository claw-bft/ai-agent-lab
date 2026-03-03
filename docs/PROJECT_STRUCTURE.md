# AI Agent Lab 项目结构

本文档说明仓库的组织结构和各目录用途。

## 目录结构

```
ai-agent-lab/
├── agent-collaboration/    # ACP协议多智能体协作
├── api/                    # REST API接口
├── claude-domain-skills/   # Claude领域技能集合（18个领域）
├── clawhub-web/           # ClawHub Web前端
├── coding-pro/            # AI代码生成器
├── context-compressor/    # 上下文压缩工具
├── data/                  # 运行时数据（.gitignore）
│   └── memory/           # 向量记忆存储
├── docs/                  # 项目文档
├── finance-pro/           # 金融数据分析
├── financial-daily/       # 每日财经简报
├── logs/                  # 日志文件（.gitignore）
│   └── iterations/       # 迭代历史报告
├── memory-enhanced/       # 向量记忆系统
├── multi-tenant/          # 多租户支持
├── notification-service/  # 通知服务
├── product-pro/           # 产品管理
├── quick-templates/       # 快速模板
├── registry/              # 技能注册表
├── reports/               # 评估报告（.gitignore）
│   └── evaluations/      # 质量评估报告
├── research-pro/          # 研究助手
├── scripts/               # 工具脚本
├── skill-cli/             # 自然语言执行层
├── skill-evaluator/       # 技能评测系统
├── skill-recommender/     # 技能推荐系统
├── skills/                # 额外技能集合
├── stock-portfolio-analyzer/  # 投资组合分析
├── temp/                  # 临时文件（.gitignore）
├── token-manager/         # 配置管理
├── vercel-deploy/         # Vercel部署工具
└── visual-reports/        # 可视化报告

## 核心文件

- `clawhub-cli.py`        # CLI入口
- `README.md`             # 项目说明
- `requirements.txt`      # Python依赖
- `PROJECT_QUALITY_REPORT.md`  # 质量报告
- `.gitignore`            # Git忽略规则

## 数据流

```
用户输入 → Skill CLI → Intent Router → 技能包 → 数据源/API
                ↓
         Memory (上下文)
                ↓
         Token Manager (配置)
```

## 开发规范

1. **技能包开发**: 每个技能包独立目录，包含 SKILL.md、测试、核心代码
2. **日志归档**: 迭代报告自动归档到 logs/iterations/
3. **数据隔离**: 运行时数据存放在 data/，不提交到版本控制
4. **测试覆盖**: 每个技能包需包含 tests/ 目录

## 自动化

- 每5分钟: 仓库健康检查
- 每10分钟: GitHub自动提交
- 每30分钟: 新闻情报抓取

## 相关链接

- [迭代报告](../logs/iterations/)
- [评估报告](../reports/evaluations/)
- [项目文档](./)
