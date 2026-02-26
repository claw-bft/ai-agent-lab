# ACP (Agent Collaboration Protocol) v0.2.0

Agent间协作协议实现 - 使多个AI Agent能够像微服务一样协同工作。

## 快速开始

```python
from acp import ACPAgent, ACPRegistry, ACPTransport, HTTPTransportAdapter

# 创建注册中心
registry = ACPRegistry()

# 创建Agent
agent = ACPAgent(
    agent_id="my_agent",
    agent_type="research",
    capabilities=["web_search", "data_analysis"],
    endpoint="http://localhost:8080",
    registry=registry
)

# 注册任务处理器
def handle_analysis(payload):
    return {"result": "analysis complete"}

agent.register_handler("analyze", handle_analysis)

# 启动传输层
transport = ACPTransport(agent, HTTPTransportAdapter(port=8080))
await transport.start()
```

## 架构

```
acp/
├── __init__.py          # 包入口
├── core.py              # 核心协议实现
├── transport.py         # 传输层适配器
└── examples/            # 示例代码
    └── research_analysis_collab.py
```

## 核心概念

### Agent
- 具有唯一ID、类型和能力列表
- 可以注册任务处理器
- 通过注册中心发现其他Agent

### 消息
- TaskRequest: 任务委托请求
- TaskResponse: 任务执行结果
- Heartbeat: 状态同步

### 传输层
- HTTPTransportAdapter: HTTP/REST接口
- RedisTransportAdapter: 消息队列 (Redis Pub/Sub)

## 协作模式

1. **直接委托**: Agent A 直接发送任务给 Agent B
2. **能力发现**: 通过注册中心查找具有特定能力的Agent
3. **异步回调**: 任务完成后通过消息返回结果

## 版本历史

- v0.2.0 (2026-02-27): 初始实现
  - 核心协议定义
  - HTTP传输层
  - Redis传输层 (预留)
  - 研究-分析协作示例
