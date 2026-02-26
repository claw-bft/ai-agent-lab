"""
Agent Collaboration Protocol (ACP) - 主入口
"""
from .message import (
    Message, MessageType, AgentInfo, TaskRequest, TaskResponse,
    TaskStatus, Priority, StatusUpdate,
    create_task_request_message, create_task_response_message,
    create_status_update_message, create_discovery_message
)
from .message_bus import MessageBus, InMemoryMessageBus, RedisMessageBus, MessageBusFactory
from .agent import Agent
from .workflow import WorkflowEngine, ParallelWorkflowEngine, Workflow, WorkflowStep, WorkflowStatus

__version__ = "0.1.0"
__all__ = [
    # 消息类型
    "Message", "MessageType", "AgentInfo", "TaskRequest", "TaskResponse",
    "TaskStatus", "Priority", "StatusUpdate",
    # 消息工厂函数
    "create_task_request_message", "create_task_response_message",
    "create_status_update_message", "create_discovery_message",
    # 消息总线
    "MessageBus", "InMemoryMessageBus", "RedisMessageBus", "MessageBusFactory",
    # Agent
    "Agent",
    # 工作流
    "WorkflowEngine", "ParallelWorkflowEngine", "Workflow", "WorkflowStep", "WorkflowStatus",
]
