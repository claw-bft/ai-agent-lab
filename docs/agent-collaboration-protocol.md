# Agent Collaboration Protocol (ACP)

## Overview

Agent Collaboration Protocol (ACP) 是一个轻量级的多Agent通信协议，旨在实现AI Agent之间的标准化消息交换、任务编排和状态同步。

## Core Concepts

### Agent Identity
每个Agent在系统中拥有唯一的身份标识：
```json
{
  "agent_id": "uuid",
  "name": "analyzer-agent",
  "capabilities": ["stock-analysis", "data-fetching"],
  "version": "1.0.0"
}
```

### Message Types

#### 1. Task Request (任务请求)
```json
{
  "type": "task_request",
  "message_id": "uuid",
  "from": "agent-a",
  "to": "agent-b",
  "timestamp": "2026-02-27T03:20:00Z",
  "payload": {
    "task_type": "stock_analysis",
    "parameters": {"symbol": "AAPL"},
    "priority": "high",
    "deadline": "2026-02-27T04:00:00Z"
  }
}
```

#### 2. Task Response (任务响应)
```json
{
  "type": "task_response",
  "message_id": "uuid",
  "in_reply_to": "original-message-id",
  "from": "agent-b",
  "to": "agent-a",
  "timestamp": "2026-02-27T03:25:00Z",
  "payload": {
    "status": "completed",
    "result": {...},
    "execution_time_ms": 300000
  }
}
```

#### 3. Status Update (状态更新)
```json
{
  "type": "status_update",
  "message_id": "uuid",
  "from": "agent-b",
  "to": "agent-a",
  "timestamp": "2026-02-27T03:22:00Z",
  "payload": {
    "task_id": "task-uuid",
    "status": "in_progress",
    "progress": 0.6,
    "message": "Fetching market data..."
  }
}
```

#### 4. Discovery (发现)
```json
{
  "type": "discovery",
  "message_id": "uuid",
  "from": "agent-a",
  "to": "broadcast",
  "timestamp": "2026-02-27T03:20:00Z",
  "payload": {
    "action": "register",
    "agent_info": {...}
  }
}
```

## Implementation

### Python SDK

```python
from acp import Agent, MessageBus, TaskRequest

# 创建Agent
agent = Agent(
    name="analyzer-agent",
    capabilities=["stock-analysis"]
)

# 定义任务处理器
@agent.handler("stock_analysis")
async def handle_stock_analysis(request: TaskRequest):
    symbol = request.parameters["symbol"]
    # 执行分析
    return {"recommendation": "buy", "confidence": 0.85}

# 发送任务
response = await agent.send_task(
    to="news-agent",
    task_type="fetch_news",
    parameters={"symbol": "AAPL"}
)
```

### Message Bus

支持多种传输后端：
- **In-Memory**: 单机多Agent
- **Redis**: 分布式部署
- **WebSocket**: 实时通信

## Workflow Example

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  news-agent │────▶│analyzer-agent│────▶│deploy-agent │
└─────────────┘     └─────────────┘     └─────────────┘
      │                    │                    │
      ▼                    ▼                    ▼
  fetch_news()      analyze_stock()      deploy_report()
```

## Status

- **Version**: 0.1.0
- **Status**: Draft
- **Last Updated**: 2026-02-27
