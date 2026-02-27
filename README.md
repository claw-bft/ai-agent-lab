# AI Agent Lab

一个完整的 AI 技能包生态系统，包含 18 个专业技能，覆盖编程、金融、产品、研究等多个领域。

[![CI/CD](https://github.com/claw-bft/ai-agent-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/claw-bft/ai-agent-lab/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 核心技能包

### 编程开发
| 技能 | 描述 | 状态 |
|------|------|------|
| [coding-pro](skills/coding-pro/) | 智能代码生成，支持 Claude/OpenAI/Kimi API | ✅ 完整 |
| [skill-cli](skills/skill-cli/) | 自然语言执行层，AI 驱动的命令行接口 | ✅ 完整 |

### 金融投资
| 技能 | 描述 | 状态 |
|------|------|------|
| [finance-pro](skills/finance-pro/) | 趋势交易、价值投资、套利策略 | ✅ 完整 |
| [stock-portfolio-analyzer](skills/stock-portfolio-analyzer/) | 股票组合分析与自动报告生成 | ✅ 完整 |

### 产品与研究
| 技能 | 描述 | 状态 |
|------|------|------|
| [product-pro](skills/product-pro/) | 市场洞察、PRD 生成、竞品分析 | ✅ 完整 |
| [research-pro](skills/research-pro/) | 跨领域研究、数据分析、自动化流程 | ✅ 完整 |

### 系统与协作
| 技能 | 描述 | 状态 |
|------|------|------|
| [agent-collaboration](skills/agent-collaboration/) | 多 Agent 协作协议 | ✅ 完整 |
| [workflow-orchestrator](skills/workflow-orchestrator/) | 可视化工作流编排 | ✅ 完整 |
| [memory-enhanced](skills/memory-enhanced/) | 向量记忆存储系统 | ✅ 完整 |
| [vercel-deploy](skills/vercel-deploy/) | 自动部署到 Vercel | ✅ 完整 |

### 领域专业知识
| 技能 | 描述 | 状态 |
|------|------|------|
| [marketing](skills/claude-domain-skills/business/marketing/) | 数字营销策略与内容营销 | ✅ 完整 |
| [product-management](skills/claude-domain-skills/business/product-management/) | PRD 撰写、OKR 设定、路线图 | ✅ 完整 |
| [business-strategy](skills/claude-domain-skills/business/strategy/) | 蓝海策略、商业模式设计 | ✅ 完整 |
| [game-design](skills/claude-domain-skills/creative/game-design/) | 游戏设计理论与机制 | ✅ 完整 |
| [storytelling](skills/claude-domain-skills/creative/storytelling/) | 叙事结构与角色塑造 | ✅ 完整 |
| [ui-ux-design](skills/claude-domain-skills/creative/ui-ux-design/) | 界面设计与用户体验 | ✅ 完整 |
| [investment-analysis](skills/claude-domain-skills/finance/investment-analysis/) | 股票分析与财报解读 | ✅ 完整 |
| [knowledge-management](skills/claude-domain-skills/professional/knowledge-management/) | 第二大脑与笔记系统 | ✅ 完整 |

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/claw-bft/ai-agent-lab.git
cd ai-agent-lab

# 安装依赖
pip install -r requirements.txt
```

### 使用示例

#### AI 代码生成

```bash
# 使用 Claude 生成 FastAPI 项目
python skills/coding-pro/ai_code_generator.py \
  "创建一个用户管理 API 服务" \
  --language python \
  --framework fastapi
```

#### 金融数据分析

```python
from skills.finance_pro.data_fetcher import StockDataFetcher

fetcher = StockDataFetcher()
data = fetcher.fetch_stock_data("AAPL", period="1y")
```

#### 自然语言执行

```bash
# 通过自然语言执行技能
python skills/skill-cli/executor.py \
  "分析苹果股票最近一年的表现"
```

## 项目统计

- **18** 个技能包
- **48** 个 Python 文件
- **16,766** 行代码
- **95%** 测试覆盖率
- **12** 个测试文件

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent Lab                             │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  skill-cli   │  │   coding-pro │  │  finance-pro │      │
│  │  (自然语言)   │  │  (代码生成)   │  │  (金融分析)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  product-pro │  │ research-pro │  │   vercel-    │      │
│  │  (产品管理)   │  │  (研究分析)   │  │   deploy     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐  │
│  │              agent-collaboration                      │  │
│  │              (多 Agent 协作协议)                       │  │
│  └──────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐  │
│  │              workflow-orchestrator                    │  │
│  │              (工作流编排引擎)                          │  │
│  └──────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐  │
│  │              memory-enhanced                          │  │
│  │              (向量记忆存储)                            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 贡献

欢迎贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

感谢所有贡献者和开源社区的支持。
