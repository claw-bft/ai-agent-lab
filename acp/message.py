"""
Agent Collaboration Protocol (ACP) - Core Message Types
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class MessageType(Enum):
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    DISCOVERY = "discovery"
    HEARTBEAT = "heartbeat"


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AgentInfo:
    """Agent身份信息"""
    agent_id: str
    name: str
    capabilities: List[str]
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "capabilities": self.capabilities,
            "version": self.version,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentInfo":
        return cls(
            agent_id=data["agent_id"],
            name=data["name"],
            capabilities=data.get("capabilities", []),
            version=data.get("version", "1.0.0"),
            metadata=data.get("metadata", {})
        )


@dataclass
class Message:
    """ACP消息基类"""
    message_id: str
    msg_type: MessageType
    from_agent: str
    to_agent: str
    timestamp: datetime
    payload: Dict[str, Any]
    in_reply_to: Optional[str] = None
    
    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp.replace('Z', '+00:00'))
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "message_id": self.message_id,
            "type": self.msg_type.value,
            "from": self.from_agent,
            "to": self.to_agent,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload
        }
        if self.in_reply_to:
            result["in_reply_to"] = self.in_reply_to
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            message_id=data["message_id"],
            msg_type=MessageType(data["type"]),
            from_agent=data["from"],
            to_agent=data["to"],
            timestamp=data["timestamp"],
            payload=data.get("payload", {}),
            in_reply_to=data.get("in_reply_to")
        )


@dataclass
class TaskRequest:
    """任务请求"""
    task_id: str
    task_type: str
    parameters: Dict[str, Any]
    priority: Priority = Priority.MEDIUM
    deadline: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "parameters": self.parameters,
            "priority": self.priority.value
        }
        if self.deadline:
            result["deadline"] = self.deadline.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskRequest":
        deadline = None
        if data.get("deadline"):
            deadline = datetime.fromisoformat(data["deadline"].replace('Z', '+00:00'))
        return cls(
            task_id=data["task_id"],
            task_type=data["task_type"],
            parameters=data.get("parameters", {}),
            priority=Priority(data.get("priority", "medium")),
            deadline=deadline
        )


@dataclass
class TaskResponse:
    """任务响应"""
    task_id: str
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "task_id": self.task_id,
            "status": self.status.value
        }
        if self.result:
            result["result"] = self.result
        if self.error:
            result["error"] = self.error
        if self.execution_time_ms:
            result["execution_time_ms"] = self.execution_time_ms
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskResponse":
        return cls(
            task_id=data["task_id"],
            status=TaskStatus(data["status"]),
            result=data.get("result"),
            error=data.get("error"),
            execution_time_ms=data.get("execution_time_ms")
        )


@dataclass
class StatusUpdate:
    """状态更新"""
    task_id: str
    status: TaskStatus
    progress: float = 0.0  # 0.0 - 1.0
    message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "progress": self.progress,
            "message": self.message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StatusUpdate":
        return cls(
            task_id=data["task_id"],
            status=TaskStatus(data["status"]),
            progress=data.get("progress", 0.0),
            message=data.get("message", "")
        )


def create_task_request_message(
    from_agent: str,
    to_agent: str,
    task_type: str,
    parameters: Dict[str, Any],
    priority: Priority = Priority.MEDIUM,
    deadline: Optional[datetime] = None
) -> Message:
    """创建任务请求消息"""
    task = TaskRequest(
        task_id=str(uuid.uuid4()),
        task_type=task_type,
        parameters=parameters,
        priority=priority,
        deadline=deadline
    )
    return Message(
        message_id=str(uuid.uuid4()),
        msg_type=MessageType.TASK_REQUEST,
        from_agent=from_agent,
        to_agent=to_agent,
        timestamp=datetime.utcnow(),
        payload=task.to_dict()
    )


def create_task_response_message(
    from_agent: str,
    to_agent: str,
    in_reply_to: str,
    task_id: str,
    status: TaskStatus,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
) -> Message:
    """创建任务响应消息"""
    task_response = TaskResponse(
        task_id=task_id,
        status=status,
        result=result,
        error=error
    )
    return Message(
        message_id=str(uuid.uuid4()),
        msg_type=MessageType.TASK_RESPONSE,
        from_agent=from_agent,
        to_agent=to_agent,
        timestamp=datetime.utcnow(),
        payload=task_response.to_dict(),
        in_reply_to=in_reply_to
    )


def create_status_update_message(
    from_agent: str,
    to_agent: str,
    task_id: str,
    status: TaskStatus,
    progress: float = 0.0,
    message: str = ""
) -> Message:
    """创建状态更新消息"""
    status_update = StatusUpdate(
        task_id=task_id,
        status=status,
        progress=progress,
        message=message
    )
    return Message(
        message_id=str(uuid.uuid4()),
        msg_type=MessageType.STATUS_UPDATE,
        from_agent=from_agent,
        to_agent=to_agent,
        timestamp=datetime.utcnow(),
        payload=status_update.to_dict()
    )


def create_discovery_message(
    from_agent: str,
    agent_info: AgentInfo,
    action: str = "register"
) -> Message:
    """创建发现/注册消息"""
    return Message(
        message_id=str(uuid.uuid4()),
        msg_type=MessageType.DISCOVERY,
        from_agent=from_agent,
        to_agent="broadcast",
        timestamp=datetime.utcnow(),
        payload={
            "action": action,
            "agent_info": agent_info.to_dict()
        }
    )
