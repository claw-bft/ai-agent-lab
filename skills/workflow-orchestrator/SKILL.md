---
name: workflow-orchestrator
description: 智能工作流编排系统 - 可视化工作流编辑器，支持多Agent协作工作流的创建、执行和监控
---

# Workflow Orchestrator

智能工作流编排系统，让用户能够通过可视化方式组合 finance-pro、research-pro、product-pro、coding-pro 等技能包，创建自定义的多Agent协作工作流。

## 核心功能

- **可视化工作流编辑器**: 拖拽式节点编辑，支持开始/结束/任务/条件/并行/聚合/延迟节点
- **预定义工作流模板**: 股票研究、产品开发、内容营销等即用模板
- **工作流执行引擎**: 支持顺序/并行/条件执行，变量替换，上下文传递
- **执行监控面板**: 实时查看工作流执行状态和节点日志
- **导入导出**: JSON格式的工作流定义导入导出

## 架构

```
workflow-orchestrator/
├── workflow_engine.py     # 工作流引擎核心
├── workflow-cli           # CLI工具
├── web-editor/            # 可视化编辑器
│   ├── index.html         # 编辑器主页面
│   └── README.md          # 编辑器文档
└── SKILL.md              # 本文档
```

### 核心组件

| 组件 | 类名 | 功能 |
|------|------|------|
| 工作流引擎 | `WorkflowEngine` | 工作流注册、执行、状态管理 |
| 工作流定义 | `WorkflowDefinition` | 节点、边、变量的完整定义 |
| 模板库 | `WorkflowTemplateLibrary` | 预定义工作流模板 |
| 执行实例 | `WorkflowExecution` | 单次执行的上下文和状态 |

### 节点类型

| 类型 | 说明 | 用途 |
|------|------|------|
| START | 开始节点 | 工作流入口 |
| END | 结束节点 | 工作流出口 |
| TASK | 任务节点 | 调用Agent执行任务 |
| CONDITION | 条件节点 | 根据条件分支 |
| PARALLEL | 并行节点 | 同时执行多个分支 |
| AGGREGATE | 聚合节点 | 合并并行结果 |
| DELAY | 延迟节点 | 延时执行 |

### 方式3: Web可视化编辑器

```bash
# 启动本地服务器
cd web-editor
python -m http.server 8080

# 访问 http://localhost:8080
```

功能特性:
- 🎨 拖拽式节点编辑
- 🔗 可视化连线
- 📋 4个预定义模板
- ⚡ 实时执行监控
- 💾 JSON导入导出
- 🖥️ 执行日志面板

使用方法:
1. 从左侧拖拽节点到画布
2. 点击节点编辑属性
3. 拖拽节点端口创建连接
4. 点击执行按钮运行工作流

## 使用方式

### 方式1: CLI工具

```bash
# 查看系统状态
./workflow-cli status

# 列出可用模板
./workflow-cli templates

# 从模板创建工作流
./workflow-cli create --template stock-research
./workflow-cli create --template product-dev --name "AI助手开发"

# 创建股票研究工作流
./workflow-cli create --stock 600519.SH

# 创建产品开发工作流
./workflow-cli create --product "智能客服系统"

# 执行工作流
./workflow-cli execute <workflow_id>
./workflow-cli execute <workflow_id> --input '{"symbol": "AAPL"}'

# 查看执行状态
./workflow-cli execution <execution_id>

# 列出执行记录
./workflow-cli executions
./workflow-cli executions --workflow <workflow_id>

# 导入导出
./workflow-cli export <workflow_id> workflow.json
./workflow-cli import workflow.json

# 运行演示
./workflow-cli demo
```

### 方式2: Python API

```python
from workflow_engine import (
    WorkflowEngine, WorkflowTemplateLibrary, WorkflowDefinition,
    WorkflowNode, WorkflowEdge, NodeType, get_workflow_engine,
    create_stock_research_workflow, create_product_dev_workflow
)

# 获取引擎
engine = get_workflow_engine()

# 从模板创建工作流
workflow = WorkflowTemplateLibrary.create_workflow_from_template(
    "stock-research", "茅台研究"
)
workflow_id = engine.register_workflow(workflow)

# 执行工作流
execution_id = engine.execute_workflow(workflow_id, {"symbol": "600519.SH"})

# 检查状态
execution = engine.get_execution(execution_id)
print(f"Status: {execution.status.value}")

# 自定义工作流
workflow = WorkflowDefinition(name="自定义工作流")

# 添加节点
start = WorkflowNode(node_type=NodeType.START, name="开始")
task1 = WorkflowNode(
    node_type=NodeType.TASK,
    name="获取行情",
    agent_id="finance-pro",
    task_type="finance.quote",
    parameters={"symbol": "${input.symbol}"}
)
end = WorkflowNode(node_type=NodeType.END, name="结束")

workflow.nodes.extend([start, task1, end])

# 添加边
workflow.edges.append(WorkflowEdge(source=start.node_id, target=task1.node_id))
workflow.edges.append(WorkflowEdge(source=task1.node_id, target=end.node_id))

# 注册并执行
workflow_id = engine.register_workflow(workflow)
exec_id = engine.execute_workflow(workflow_id, {"symbol": "AAPL"})
```

## 预定义模板

### 1. 股票研究 (stock-research)

```
开始 → 获取行情(finance.quote) → 公司研究(research.search) → 深度分析(research.deep) → 完成
```

参与Agent:
- `finance-pro`: 获取股票实时行情
- `research-pro`: 公司背景研究、深度分析

### 2. 产品开发 (product-dev)

```
开始 → 市场调研(research.search) → 竞品分析(product.competitor) → 生成PRD(product.prd) → 原型代码(coding.generate) → 完成
```

参与Agent:
- `research-pro`: 市场调研
- `product-pro`: 竞品分析、PRD生成
- `coding-pro`: 生成原型代码

### 3. 内容营销 (content-marketing)

```
开始 → 话题研究(research.search) → 深度研究(research.deep) → 生成报告(research.report) → 完成
```

参与Agent:
- `research-pro`: 研究、报告生成

## 工作流定义格式

```json
{
  "workflow_id": "uuid",
  "name": "股票研究 - AAPL",
  "description": "对 AAPL 进行全面的股票研究分析",
  "version": "1.0.0",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "nodes": [
    {
      "node_id": "abc123",
      "node_type": "start",
      "name": "开始",
      "position": {"x": 100, "y": 200}
    },
    {
      "node_id": "def456",
      "node_type": "task",
      "name": "获取股票行情",
      "agent_id": "finance-pro",
      "task_type": "finance.quote",
      "parameters": {"symbol": "AAPL"},
      "position": {"x": 300, "y": 200}
    },
    {
      "node_id": "ghi789",
      "node_type": "end",
      "name": "完成",
      "position": {"x": 500, "y": 200}
    }
  ],
  "edges": [
    {"edge_id": "e1", "source": "abc123", "target": "def456"},
    {"edge_id": "e2", "source": "def456", "target": "ghi789"}
  ],
  "variables": {},
  "tags": ["stock", "research"]
}
```

## 变量替换

在节点参数中可以使用 `${path.to.value}` 语法引用上下文中的值：

```python
# 节点参数
parameters={"symbol": "${input.symbol}", "query": "${node_abc123_result.name}"}

# 执行时传入
engine.execute_workflow(workflow_id, {"symbol": "AAPL"})
```

上下文结构：
```json
{
  "input": {"symbol": "AAPL"},
  "node_abc123_result": {"name": "Apple Inc", "price": 150.0},
  "node_def456_result": {...}
}
```

## 与Agent Collaboration集成

```python
from agent_protocol import create_collaboration_system
from skill_adapters import create_skill_agents
from workflow_engine import get_workflow_engine

# 创建协作系统
agents, registry, bus, orchestrator = create_skill_agents()

# 获取工作流引擎
engine = get_workflow_engine()

# 注册任务处理器
def handle_finance_quote(params):
    return agents["finance"]._get_stock_quote(params.get("symbol"))

def handle_research_search(params):
    return agents["research"]._search(params.get("query"))

engine.register_task_handler("finance.quote", handle_finance_quote)
engine.register_task_handler("research.search", handle_research_search)

# 执行工作流
workflow = create_stock_research_workflow("600519.SH")
workflow_id = engine.register_workflow(workflow)
exec_id = engine.execute_workflow(workflow_id)
```

## 扩展新模板

```python
from workflow_engine import WorkflowTemplateLibrary

# 添加新模板
WorkflowTemplateLibrary.TEMPLATES["my-template"] = {
    "name": "我的模板",
    "description": "模板描述",
    "nodes": [
        {"node_type": "start", "name": "开始", "position": {"x": 100, "y": 100}},
        {"node_type": "task", "name": "任务1", "agent_id": "research-pro", "task_type": "research.search", "position": {"x": 300, "y": 100}},
        {"node_type": "end", "name": "完成", "position": {"x": 500, "y": 100}}
    ],
    "edges": [
        {"source": "node_0", "target": "node_1"},
        {"source": "node_1", "target": "node_2"}
    ]
}
```

## 更新日志

### 2026-02-27
- ✅ 实现工作流引擎核心 (workflow_engine.py)
- ✅ 实现7种节点类型 (START/END/TASK/CONDITION/PARALLEL/AGGREGATE/DELAY)
- ✅ 创建CLI工具 (workflow-cli)
- ✅ 实现3个预定义模板 (stock-research, product-dev, content-marketing)
- ✅ 支持变量替换和上下文传递
- ✅ 支持工作流导入导出
- ✅ **实现可视化Web编辑器 (web-editor/)**
- ✅ 支持拖拽式节点编辑和连线
- ✅ 添加执行监控面板和日志
- ✅ 支持JSON工作流导入导出
