from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class HealthStatus(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime
    uptime_seconds: Optional[float] = None


class MessageType(str, Enum):
    """Session message types"""
    SESSION = "session"
    MESSAGE = "message"
    MODEL_CHANGE = "model_change"
    THINKING_LEVEL_CHANGE = "thinking_level_change"
    CUSTOM = "custom"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"


class SessionInfo(BaseModel):
    """Basic session information"""
    id: str
    session_key: Optional[str] = None
    status: str = "unknown"  # active, completed, error
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    message_count: int = 0
    file_size: int = 0
    file_path: Optional[str] = None
    is_locked: bool = False


class SessionDetail(SessionInfo):
    """Detailed session information"""
    messages: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
    model: Optional[str] = None
    provider: Optional[str] = None


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class TaskInfo(BaseModel):
    """Task information"""
    id: str
    name: Optional[str] = None
    task_type: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    requester: Optional[str] = None
    workflow: Optional[str] = None
    steps: List[Dict[str, Any]] = []
    file_path: Optional[str] = None


class AgentStatus(str, Enum):
    """Agent operational status"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class AgentInfo(BaseModel):
    """Agent information"""
    id: str
    name: str
    description: Optional[str] = None
    status: AgentStatus = AgentStatus.IDLE
    skills: List[str] = []
    active_sessions: int = 0
    total_sessions: int = 0
    last_active: Optional[datetime] = None
    capabilities: List[str] = []


class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StatsSummary(BaseModel):
    """Dashboard statistics summary"""
    total_sessions: int
    active_sessions: int
    total_tasks: int
    pending_tasks: int
    running_tasks: int
    total_agents: int
    busy_agents: int
