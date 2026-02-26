# Agent Collaboration Protocol (ACP) v0.2.0

Agent间协作协议 - 标准化多Agent通信与任务委托机制

## 概述

ACP (Agent Collaboration Protocol) 定义了多个AI Agent之间的标准化通信接口，使Agent能够像微服务一样协同工作。

## 核心概念

### 1. Agent身份
- **agent_id**: 全局唯一标识符
- **agent_type**: Agent类型 (research, analysis, coding, etc.)
- **capabilities**: 能力列表
- **endpoint**: 通信端点

### 2. 消息类型

#### TaskRequest - 任务委托
```json
{
  "message_type": "task_request",
  "message_id": "uuid",
  "from_agent": "agent_a",
  "to_agent": "agent_b",
  "task": {
    "task_id": "uuid",
    "task_type": "analysis",
    "payload": {},
    "priority": "high",
    "timeout_ms": 60000
  },
  "timestamp": "2026-02-27T04:00:00Z"
}
```

#### TaskResponse - 任务结果
```json
{
  "message_type": "task_response",
  "message_id": "uuid",
  "in_reply_to": "original_message_id",
  "from_agent": "agent_b",
  "to_agent": "agent_a",
  "task_id": "uuid",
  "result": {
    "status": "success|failure|timeout",
    "data": {},
    "error": null
  },
  "timestamp": "2026-02-27T04:01:00Z"
}
```

#### Heartbeat - 状态同步
```json
{
  "message_type": "heartbeat",
  "agent_id": "agent_a",
  "status": "idle|busy|error",
  "active_tasks": [],
  "timestamp": "2026-02-27T04:00:00Z"
}
```

### 3. 协作模式

#### 模式1: 直接委托
```
Agent A -> TaskRequest -> Agent B
Agent A <- TaskResponse <- Agent B
```

#### 模式2: 广播订阅
```
Agent A -> Broadcast -> Message Queue
Agent B, C, D <- Subscribe <- Message Queue
```

#### 模式3: 主从协调
```
Coordinator Agent -> 任务拆分 -> Worker Agents
Coordinator Agent <- 结果聚合 <- Worker Agents
```

## 实现组件

### 1. ACP核心库 (acp/core.py)
- Agent注册与发现
- 消息路由
- 序列化/反序列化

### 2. 传输层 (acp/transport.py)
- HTTP/WebSocket接口
- 消息队列适配器 (Redis/RabbitMQ)

### 3. 示例实现 (acp/examples/)
- 研究Agent委托分析Agent
- 多Agent协作工作流

## 版本历史

- v0.2.0 (2026-02-27): 初始协议定义
