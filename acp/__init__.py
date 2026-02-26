"""
ACP - Agent Collaboration Protocol

多Agent协作协议Python实现
"""

__version__ = "0.2.0"
__author__ = "AI Agent Lab"

from .core import (
    ACPMessage,
    ACPRegistry,
    ACPAgent,
    AgentInfo,
    TaskRequest,
    TaskResult,
    MessageType,
    TaskStatus,
    AgentStatus
)

from .transport import (
    TransportAdapter,
    HTTPTransportAdapter,
    RedisTransportAdapter,
    ACPTransport
)

__all__ = [
    # 版本
    "__version__",
    
    # 核心类
    "ACPMessage",
    "ACPRegistry",
    "ACPAgent",
    "AgentInfo",
    "TaskRequest",
    "TaskResult",
    
    # 枚举
    "MessageType",
    "TaskStatus",
    "AgentStatus",
    
    # 传输层
    "TransportAdapter",
    "HTTPTransportAdapter",
    "RedisTransportAdapter",
    "ACPTransport"
]
