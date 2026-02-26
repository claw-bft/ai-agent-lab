# Agent Collaboration Protocol (ACP)

A lightweight protocol for multi-agent communication and task orchestration.

## Features

- **Message-based communication**: Standardized JSON message format
- **Task orchestration**: Workflow support for multi-step agent collaboration  
- **Pluggable transport**: In-memory, Redis, WebSocket backends
- **Async/await**: Built on Python asyncio
- **Type hints**: Full type annotation support

## Quick Start

```python
from acp import Agent, InMemoryMessageBus

# Shared message bus
bus = InMemoryMessageBus()

# Create agents
agent_a = Agent(name="agent-a", capabilities=["analyze"], message_bus=bus)
agent_b = Agent(name="agent-b", capabilities=["fetch"], message_bus=bus)

# Define handler
@agent_b.handler("fetch_data")
async def handle_fetch(request):
    return {"data": "example"}

# Send task
response = await agent_a.send_task(
    to="agent-b",
    task_type="fetch_data",
    parameters={"query": "example"}
)
```

## Documentation

- [Protocol Specification](docs/agent-collaboration-protocol.md)
- [Example Workflow](examples/acp_stock_workflow.py)

## Status

- Version: 0.1.0
- Status: Draft / Experimental
