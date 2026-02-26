---
name: agent-collaboration
description: Agent间协作协议 - 支持多Agent协同工作的标准化通信协议
---

# Agent Collaboration Protocol (ACP)

Agent间协作协议，定义标准化的Agent通信机制，支持多Agent协同工作。让 finance-pro、coding-pro、product-pro、research-pro 四个专业技能包能够无缝协作。

## 核心功能

- **消息总线**: 基于内存的高性能消息传递
- **Agent注册中心**: 动态发现和管理Agent
- **任务编排器**: 支持顺序/并行/条件执行的任务编排
- **结果聚合器**: 智能合并多Agent结果，支持冲突解决
- **工作流引擎**: 预定义的多Agent协作工作流

## 架构

```
agent-collaboration/
├── agent_protocol.py      # 核心协议实现
├── skill_adapters.py      # 技能包适配器
├── agent-collab           # CLI工具
└── SKILL.md              # 本文档
```

### 核心组件

| 组件 | 类名 | 功能 |
|------|------|------|
| Agent注册中心 | `AgentRegistry` | Agent注册、发现、心跳管理 |
| 消息总线 | `MessageBus` | 点对点/广播消息传递 |
| 任务编排器 | `TaskOrchestrator` | 任务创建、分配、依赖管理 |
| 结果聚合器 | `ResultAggregator` | 结果合并、冲突解决 |
| 协作Agent基类 | `CollaborationAgent` | Agent实现基类 |

## 使用方式

### 方式1: CLI工具

```bash
# 查看系统状态
./agent-collab status

# 列出所有Agent
./agent-collab agents

# 创建任务
./agent-collab task \
  --type finance.quote \
  --description "查询茅台股票" \
  --agent finance-pro \
  --wait 5

# 执行股票研究工作流
./agent-collab workflow \
  --type stock-research \
  --symbol 600519.SH \
  --monitor 10

# 执行产品开发工作流
./agent-collab workflow \
  --type product-dev \
  --product "AI代码助手" \
  --monitor 20

# 运行演示
./agent-collab demo
```

### 方式2: Python API

```python
from agent_protocol import create_collaboration_system
from skill_adapters import create_skill_agents

# 创建协作系统
agents, registry, bus, orchestrator = create_skill_agents()

# 创建任务
task = orchestrator.create_task(
    task_type="finance.quote",
    description="查询茅台股票",
    parameters={"symbol": "600519.SH"}
)

# 分配任务
orchestrator.assign_task(task.task_id, "finance-pro")

# 创建工作流
workflow_id = agents["master"].create_stock_research_workflow("600519.SH")

# 检查状态
status = agents["master"].get_workflow_status(workflow_id)
```

## 预定义工作流

### 1. 股票研究工作流 (stock-research)

```
finance.quote → research.search → research.deep
     ↓              ↓                  ↓
  获取股票数据   研究公司背景      深度分析报告
```

参与Agent:
- `finance-pro`: 获取股票报价
- `research-pro`: 公司背景研究、深度分析

### 2. 产品开发工作流 (product-dev)

```
research.search → product.competitor → product.prd → coding.generate
       ↓                ↓                  ↓               ↓
    市场调研         竞品分析          生成PRD        原型代码
```

参与Agent:
- `research-pro`: 市场调研
- `product-pro`: 竞品分析、PRD生成
- `coding-pro`: 生成原型代码

## 扩展新Agent

```python
from agent_protocol import CollaborationAgent, AgentRole

class MyAgent(CollaborationAgent):
    def __init__(self, registry, message_bus):
        super().__init__(
            agent_id="my-agent",
            role=AgentRole.SPECIALIST,
            capabilities=["my-skill"],
            registry=registry,
            message_bus=message_bus
        )
    
    def _handle_task(self, message):
        # 处理任务
        task_id = message.payload.get("task_id")
        # ... 执行任务 ...
        self.send_result(task_id, {"result": "..."})
```

## 消息协议

### 消息类型

- `TASK`: 任务分配
- `RESULT`: 任务结果
- `QUERY`: 查询请求
- `RESPONSE`: 查询响应
- `EVENT`: 事件通知
- `HEARTBEAT`: 心跳
- `ERROR`: 错误

### 消息格式

```json
{
  "msg_id": "uuid",
  "msg_type": "TASK",
  "sender": "agent-id",
  "receiver": "target-agent",
  "timestamp": "2024-01-01T00:00:00",
  "payload": {...},
  "correlation_id": "task-uuid",
  "priority": 5
}
```

## 任务状态

- `PENDING`: 待处理
- `ASSIGNED`: 已分配
- `RUNNING`: 运行中
- `COMPLETED`: 已完成
- `FAILED`: 失败
- `CANCELLED`: 已取消

## 已注册Agent

| Agent ID | 角色 | 能力 |
|----------|------|------|
| finance-pro | Specialist | finance, stock, quote, analysis, portfolio |
| coding-pro | Specialist | coding, generate, review, debug, refactor |
| product-pro | Specialist | product, competitor, prd, roadmap, strategy |
| research-pro | Specialist | research, search, deep, report, synthesize |
| master-orchestrator | Orchestrator | orchestrate, coordinate, plan |

## 更新日志

### 2026-02-27
- ✅ 实现Agent间协作协议核心 (agent_protocol.py)
- ✅ 实现技能包适配器层 (skill_adapters.py)
- ✅ 创建CLI工具 (agent-collab)
- ✅ 实现股票研究工作流
- ✅ 实现产品开发工作流
- ✅ 支持任务依赖和并行执行
