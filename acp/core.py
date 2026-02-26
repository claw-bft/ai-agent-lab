"""
ACP Core - Agent Collaboration Protocol核心实现
"""
import json
import uuid
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


class MessageType(Enum):
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    HEARTBEAT = "heartbeat"
    AGENT_REGISTER = "agent_register"
    AGENT_DISCOVER = "agent_discover"


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"


class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


@dataclass
class AgentInfo:
    """Agent注册信息"""
    agent_id: str
    agent_type: str
    capabilities: List[str]
    endpoint: str
    status: str = "idle"
    last_heartbeat: float = 0.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TaskRequest:
    """任务委托请求"""
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    priority: str = "normal"
    timeout_ms: int = 60000
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TaskResult:
    """任务执行结果"""
    status: str
    data: Optional[Dict] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ACPMessage:
    """ACP标准消息格式"""
    message_type: str
    message_id: str
    from_agent: str
    to_agent: str
    timestamp: str
    payload: Dict[str, Any]
    in_reply_to: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        msg_type: MessageType,
        from_agent: str,
        to_agent: str,
        payload: Dict,
        reply_to: Optional[str] = None
    ) -> "ACPMessage":
        return cls(
            message_type=msg_type.value,
            message_id=str(uuid.uuid4()),
            from_agent=from_agent,
            to_agent=to_agent,
            timestamp=datetime.utcnow().isoformat() + "Z",
            payload=payload,
            in_reply_to=reply_to
        )
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str) -> "ACPMessage":
        data = json.loads(json_str)
        return cls(**data)


class ACPRegistry:
    """Agent注册中心"""
    
    def __init__(self):
        self._agents: Dict[str, AgentInfo] = {}
        self._capabilities_index: Dict[str, List[str]] = {}
    
    def register(self, agent_info: AgentInfo) -> bool:
        """注册Agent"""
        self._agents[agent_info.agent_id] = agent_info
        
        # 更新能力索引
        for cap in agent_info.capabilities:
            if cap not in self._capabilities_index:
                self._capabilities_index[cap] = []
            if agent_info.agent_id not in self._capabilities_index[cap]:
                self._capabilities_index[cap].append(agent_info.agent_id)
        
        return True
    
    def unregister(self, agent_id: str) -> bool:
        """注销Agent"""
        if agent_id not in self._agents:
            return False
        
        agent = self._agents[agent_id]
        
        # 从能力索引中移除
        for cap in agent.capabilities:
            if cap in self._capabilities_index:
                if agent_id in self._capabilities_index[cap]:
                    self._capabilities_index[cap].remove(agent_id)
        
        del self._agents[agent_id]
        return True
    
    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """获取Agent信息"""
        return self._agents.get(agent_id)
    
    def find_by_capability(self, capability: str) -> List[AgentInfo]:
        """按能力查找Agent"""
        agent_ids = self._capabilities_index.get(capability, [])
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]
    
    def list_agents(self) -> List[AgentInfo]:
        """列出所有Agent"""
        return list(self._agents.values())
    
    def update_heartbeat(self, agent_id: str) -> bool:
        """更新心跳"""
        if agent_id not in self._agents:
            return False
        self._agents[agent_id].last_heartbeat = time.time()
        return True
    
    def cleanup_offline(self, timeout_seconds: float = 300) -> List[str]:
        """清理离线Agent"""
        now = time.time()
        offline = []
        for agent_id, agent in list(self._agents.items()):
            if now - agent.last_heartbeat > timeout_seconds:
                offline.append(agent_id)
                self.unregister(agent_id)
        return offline


class ACPAgent:
    """ACP Agent基类"""
    
    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        capabilities: List[str],
        endpoint: str,
        registry: Optional[ACPRegistry] = None
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.endpoint = endpoint
        self.registry = registry or ACPRegistry()
        self.status = AgentStatus.IDLE
        self._handlers: Dict[str, Callable] = {}
        self._pending_tasks: Dict[str, Any] = {}
        
        # 注册自己
        self._register_self()
    
    def _register_self(self):
        """向注册中心注册"""
        info = AgentInfo(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            capabilities=self.capabilities,
            endpoint=self.endpoint
        )
        self.registry.register(info)
    
    def register_handler(self, task_type: str, handler: Callable):
        """注册任务处理器"""
        self._handlers[task_type] = handler
    
    def create_task_request(
        self,
        to_agent: str,
        task_type: str,
        payload: Dict,
        priority: str = "normal",
        timeout_ms: int = 60000
    ) -> ACPMessage:
        """创建任务委托消息"""
        task = TaskRequest(
            task_id=str(uuid.uuid4()),
            task_type=task_type,
            payload=payload,
            priority=priority,
            timeout_ms=timeout_ms
        )
        
        return ACPMessage.create(
            msg_type=MessageType.TASK_REQUEST,
            from_agent=self.agent_id,
            to_agent=to_agent,
            payload=task.to_dict()
        )
    
    def create_task_response(
        self,
        to_agent: str,
        original_msg_id: str,
        task_id: str,
        result: TaskResult
    ) -> ACPMessage:
        """创建任务响应消息"""
        return ACPMessage.create(
            msg_type=MessageType.TASK_RESPONSE,
            from_agent=self.agent_id,
            to_agent=to_agent,
            payload={
                "task_id": task_id,
                "result": result.to_dict()
            },
            reply_to=original_msg_id
        )
    
    def create_heartbeat(self) -> ACPMessage:
        """创建心跳消息"""
        return ACPMessage.create(
            msg_type=MessageType.HEARTBEAT,
            from_agent=self.agent_id,
            to_agent="registry",
            payload={
                "status": self.status.value,
                "active_tasks": list(self._pending_tasks.keys())
            }
        )
    
    def handle_message(self, message: ACPMessage) -> Optional[ACPMessage]:
        """处理收到的消息"""
        if message.to_agent != self.agent_id and message.to_agent != "*":
            return None
        
        msg_type = message.message_type
        
        if msg_type == MessageType.TASK_REQUEST.value:
            return self._handle_task_request(message)
        elif msg_type == MessageType.TASK_RESPONSE.value:
            return self._handle_task_response(message)
        elif msg_type == MessageType.HEARTBEAT.value:
            return self._handle_heartbeat(message)
        
        return None
    
    def _handle_task_request(self, message: ACPMessage) -> Optional[ACPMessage]:
        """处理任务请求"""
        task_data = message.payload
        task_type = task_data.get("task_type")
        task_id = task_data.get("task_id")
        
        if task_type not in self._handlers:
            # 无法处理此任务类型
            result = TaskResult(
                status=TaskStatus.FAILURE.value,
                error=f"Unknown task type: {task_type}"
            )
            return self.create_task_response(
                to_agent=message.from_agent,
                original_msg_id=message.message_id,
                task_id=task_id,
                result=result
            )
        
        try:
            self.status = AgentStatus.BUSY
            self._pending_tasks[task_id] = task_data
            
            # 执行处理器
            handler = self._handlers[task_type]
            result_data = handler(task_data.get("payload", {}))
            
            result = TaskResult(
                status=TaskStatus.SUCCESS.value,
                data=result_data
            )
        except Exception as e:
            result = TaskResult(
                status=TaskStatus.FAILURE.value,
                error=str(e)
            )
        finally:
            self._pending_tasks.pop(task_id, None)
            if not self._pending_tasks:
                self.status = AgentStatus.IDLE
        
        return self.create_task_response(
            to_agent=message.from_agent,
            original_msg_id=message.message_id,
            task_id=task_id,
            result=result
        )
    
    def _handle_task_response(self, message: ACPMessage) -> None:
        """处理任务响应"""
        # 可以在这里实现回调机制
        pass
    
    def _handle_heartbeat(self, message: ACPMessage) -> None:
        """处理心跳"""
        agent_id = message.from_agent
        self.registry.update_heartbeat(agent_id)
    
    def find_agents_by_capability(self, capability: str) -> List[AgentInfo]:
        """查找具有特定能力的Agent"""
        return self.registry.find_by_capability(capability)


__all__ = [
    "ACPMessage",
    "ACPRegistry",
    "ACPAgent",
    "AgentInfo",
    "TaskRequest",
    "TaskResult",
    "MessageType",
    "TaskStatus",
    "AgentStatus"
]
