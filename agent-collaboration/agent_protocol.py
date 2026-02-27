"""
Agent间协作协议 - Agent Collaboration Protocol (ACP)

定义标准化的Agent通信协议，支持多Agent协同工作。
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import json
import uuid
import asyncio
from collections import defaultdict


class MessageType(Enum):
    """消息类型"""
    TASK = auto()           # 任务分配
    RESULT = auto()         # 任务结果
    QUERY = auto()          # 查询请求
    RESPONSE = auto()       # 查询响应
    EVENT = auto()          # 事件通知
    HEARTBEAT = auto()      # 心跳
    ERROR = auto()          # 错误


class TaskStatus(Enum):
    """任务状态"""
    PENDING = auto()        # 待处理
    ASSIGNED = auto()       # 已分配
    RUNNING = auto()        # 运行中
    COMPLETED = auto()      # 已完成
    FAILED = auto()         # 失败
    CANCELLED = auto()      # 已取消


class AgentRole(Enum):
    """Agent角色"""
    ORCHESTRATOR = "orchestrator"   # 编排器
    WORKER = "worker"               # 工作者
    SPECIALIST = "specialist"       # 专家
    OBSERVER = "observer"           # 观察者


@dataclass
class AgentMessage:
    """Agent间消息"""
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    msg_type: MessageType = MessageType.TASK
    sender: str = ""
    receiver: str = ""  # 空表示广播
    timestamp: datetime = field(default_factory=datetime.now)
    payload: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None  # 关联ID，用于请求-响应配对
    priority: int = 5  # 1-10，数字越小优先级越高
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "msg_id": self.msg_id,
            "msg_type": self.msg_type.name,
            "sender": self.sender,
            "receiver": self.receiver,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "priority": self.priority
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        return cls(
            msg_id=data["msg_id"],
            msg_type=MessageType[data["msg_type"]],
            sender=data["sender"],
            receiver=data["receiver"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            payload=data["payload"],
            correlation_id=data.get("correlation_id"),
            priority=data.get("priority", 5)
        )
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


@dataclass
class Task:
    """任务定义"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    task_type: str = ""  # 如: finance.quote, research.deep, coding.generate
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[str] = None
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)  # 依赖的任务ID
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "description": self.description,
            "parameters": self.parameters,
            "status": self.status.name,
            "assigned_to": self.assigned_to,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "dependencies": self.dependencies
        }


class AgentRegistry:
    """Agent注册中心"""
    
    def __init__(self):
        self._agents: Dict[str, Dict[str, Any]] = {}
        self._capabilities: Dict[str, List[str]] = defaultdict(list)
    
    def register(self, agent_id: str, role: AgentRole, 
                 capabilities: List[str], metadata: Dict[str, Any] = None):
        """注册Agent"""
        self._agents[agent_id] = {
            "agent_id": agent_id,
            "role": role.value,
            "capabilities": capabilities,
            "metadata": metadata or {},
            "registered_at": datetime.now().isoformat(),
            "last_heartbeat": datetime.now().isoformat(),
            "status": "online"
        }
        for cap in capabilities:
            self._capabilities[cap].append(agent_id)
    
    def unregister(self, agent_id: str):
        """注销Agent"""
        if agent_id in self._agents:
            capabilities = self._agents[agent_id]["capabilities"]
            for cap in capabilities:
                if agent_id in self._capabilities[cap]:
                    self._capabilities[cap].remove(agent_id)
            del self._agents[agent_id]
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取Agent信息"""
        return self._agents.get(agent_id)
    
    def find_agents_by_capability(self, capability: str) -> List[str]:
        """根据能力查找Agent"""
        return self._capabilities.get(capability, [])
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """列出所有Agent"""
        return list(self._agents.values())
    
    def update_heartbeat(self, agent_id: str):
        """更新心跳"""
        if agent_id in self._agents:
            self._agents[agent_id]["last_heartbeat"] = datetime.now().isoformat()


class MessageBus:
    """消息总线 - 内存实现"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._message_history: List[AgentMessage] = []
        self._max_history = 1000
    
    def subscribe(self, agent_id: str, handler: Callable[[AgentMessage], None]):
        """订阅消息"""
        self._subscribers[agent_id].append(handler)
    
    def unsubscribe(self, agent_id: str, handler: Callable[[AgentMessage], None]):
        """取消订阅"""
        if agent_id in self._subscribers:
            if handler in self._subscribers[agent_id]:
                self._subscribers[agent_id].remove(handler)
    
    def publish(self, message: AgentMessage):
        """发布消息"""
        self._message_history.append(message)
        if len(self._message_history) > self._max_history:
            self._message_history = self._message_history[-self._max_history:]
        
        # 分发消息
        if message.receiver:
            # 点对点
            if message.receiver in self._subscribers:
                for handler in self._subscribers[message.receiver]:
                    try:
                        handler(message)
                    except Exception as e:
                        print(f"Error handling message: {e}")
        else:
            # 广播
            for agent_id, handlers in self._subscribers.items():
                for handler in handlers:
                    try:
                        handler(message)
                    except Exception as e:
                        print(f"Error handling broadcast: {e}")
    
    def get_history(self, limit: int = 100) -> List[AgentMessage]:
        """获取消息历史"""
        return self._message_history[-limit:]


class TaskOrchestrator:
    """任务编排器"""
    
    def __init__(self, registry: AgentRegistry, message_bus: MessageBus):
        self.registry = registry
        self.message_bus = message_bus
        self._tasks: Dict[str, Task] = {}
        self._callbacks: Dict[str, Callable] = {}
    
    def create_task(self, task_type: str, description: str,
                   parameters: Dict[str, Any] = None,
                   created_by: str = "",
                   dependencies: List[str] = None) -> Task:
        """创建任务"""
        task = Task(
            task_type=task_type,
            description=description,
            parameters=parameters or {},
            created_by=created_by,
            dependencies=dependencies or []
        )
        self._tasks[task.task_id] = task
        return task
    
    def assign_task(self, task_id: str, agent_id: str) -> bool:
        """分配任务给Agent"""
        if task_id not in self._tasks:
            return False
        
        task = self._tasks[task_id]
        task.assigned_to = agent_id
        task.status = TaskStatus.ASSIGNED
        
        # 发送任务消息
        message = AgentMessage(
            msg_type=MessageType.TASK,
            sender="orchestrator",
            receiver=agent_id,
            payload={
                "task_id": task.task_id,
                "task_type": task.task_type,
                "description": task.description,
                "parameters": task.parameters
            },
            correlation_id=task.task_id
        )
        self.message_bus.publish(message)
        return True
    
    def execute_parallel(self, tasks: List[Task]) -> List[str]:
        """并行执行多个任务"""
        task_ids = []
        for task in tasks:
            self._tasks[task.task_id] = task
            # 查找合适的Agent
            capability = task.task_type.split(".")[0]
            agents = self.registry.find_agents_by_capability(capability)
            
            if agents:
                self.assign_task(task.task_id, agents[0])
            task_ids.append(task.task_id)
        return task_ids
    
    def execute_sequential(self, tasks: List[Task]) -> List[str]:
        """串行执行多个任务"""
        task_ids = []
        prev_task_id = None
        
        for task in tasks:
            if prev_task_id:
                task.dependencies.append(prev_task_id)
            self._tasks[task.task_id] = task
            task_ids.append(task.task_id)
            prev_task_id = task.task_id
        
        # 启动第一个任务
        if tasks:
            capability = tasks[0].task_type.split(".")[0]
            agents = self.registry.find_agents_by_capability(capability)
            if agents:
                self.assign_task(tasks[0].task_id, agents[0])
        
        return task_ids
    
    def on_task_complete(self, task_id: str, callback: Callable[[Task], None]):
        """注册任务完成回调"""
        self._callbacks[task_id] = callback
    
    def handle_result(self, message: AgentMessage):
        """处理任务结果"""
        if message.msg_type != MessageType.RESULT:
            return
        
        payload = message.payload
        task_id = payload.get("task_id")
        
        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.status = TaskStatus.COMPLETED if not payload.get("error") else TaskStatus.FAILED
            task.result = payload.get("result")
            task.error = payload.get("error")
            task.completed_at = datetime.now()
            
            # 触发回调
            if task_id in self._callbacks:
                self._callbacks[task_id](task)
            
            # 检查依赖此任务的其他任务
            self._check_dependent_tasks(task_id)
    
    def _check_dependent_tasks(self, completed_task_id: str):
        """检查并启动依赖任务"""
        for task in self._tasks.values():
            if completed_task_id in task.dependencies:
                task.dependencies.remove(completed_task_id)
                if not task.dependencies and task.status == TaskStatus.PENDING:
                    capability = task.task_type.split(".")[0]
                    agents = self.registry.find_agents_by_capability(capability)
                    if agents:
                        self.assign_task(task.task_id, agents[0])
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        if task_id in self._tasks:
            return self._tasks[task_id].status
        return None
    
    def get_all_tasks(self) -> List[Task]:
        """获取所有任务"""
        return list(self._tasks.values())


class ResultAggregator:
    """结果聚合器"""
    
    @staticmethod
    def merge_dicts(results: List[Dict[str, Any]], 
                   strategy: str = "append") -> Dict[str, Any]:
        """合并字典结果"""
        if strategy == "append":
            merged = {}
            for i, result in enumerate(results):
                for key, value in result.items():
                    new_key = f"{key}_{i}" if key in merged else key
                    merged[new_key] = value
            return merged
        elif strategy == "override":
            merged = {}
            for result in results:
                merged.update(result)
            return merged
        elif strategy == "list":
            return {"results": results}
        return {"results": results}
    
    @staticmethod
    def resolve_conflicts(results: List[Dict[str, Any]], 
                         confidence_key: str = "confidence") -> Dict[str, Any]:
        """基于置信度解决冲突"""
        if not results:
            return {}
        
        # 选择置信度最高的结果
        best_result = max(results, 
                         key=lambda x: x.get(confidence_key, 0))
        return best_result
    
    @staticmethod
    def summarize_text_results(results: List[str], 
                              max_length: int = 500) -> str:
        """总结文本结果"""
        combined = "\n\n".join(results)
        if len(combined) <= max_length:
            return combined
        return combined[:max_length] + "..."


class CollaborationAgent:
    """协作Agent基类"""
    
    def __init__(self, agent_id: str, role: AgentRole,
                 capabilities: List[str], registry: AgentRegistry,
                 message_bus: MessageBus):
        self.agent_id = agent_id
        self.role = role
        self.capabilities = capabilities
        self.registry = registry
        self.message_bus = message_bus
        self._running = False
        
        # 注册自己
        self.registry.register(agent_id, role, capabilities)
        self.message_bus.subscribe(agent_id, self._handle_message)
    
    def _handle_message(self, message: AgentMessage):
        """处理收到的消息"""
        if message.msg_type == MessageType.TASK:
            self._handle_task(message)
        elif message.msg_type == MessageType.QUERY:
            self._handle_query(message)
        elif message.msg_type == MessageType.EVENT:
            self._handle_event(message)
    
    def _handle_task(self, message: AgentMessage):
        """处理任务消息 - 子类应重写"""
        pass
    
    def _handle_query(self, message: AgentMessage):
        """处理查询消息 - 子类应重写"""
        pass
    
    def _handle_event(self, message: AgentMessage):
        """处理事件消息 - 子类可重写"""
        pass
    
    def send_result(self, task_id: str, result: Dict[str, Any],
                   receiver: str = "orchestrator"):
        """发送任务结果"""
        message = AgentMessage(
            msg_type=MessageType.RESULT,
            sender=self.agent_id,
            receiver=receiver,
            payload={
                "task_id": task_id,
                "result": result
            },
            correlation_id=task_id
        )
        self.message_bus.publish(message)
    
    def send_error(self, task_id: str, error: str,
                  receiver: str = "orchestrator"):
        """发送错误"""
        message = AgentMessage(
            msg_type=MessageType.ERROR,
            sender=self.agent_id,
            receiver=receiver,
            payload={
                "task_id": task_id,
                "error": error
            },
            correlation_id=task_id
        )
        self.message_bus.publish(message)
    
    def query(self, target: str, query_type: str, 
             parameters: Dict[str, Any]) -> str:
        """向其他Agent发送查询"""
        correlation_id = str(uuid.uuid4())[:8]
        message = AgentMessage(
            msg_type=MessageType.QUERY,
            sender=self.agent_id,
            receiver=target,
            payload={
                "query_type": query_type,
                "parameters": parameters
            },
            correlation_id=correlation_id
        )
        self.message_bus.publish(message)
        return correlation_id
    
    def start(self):
        """启动Agent"""
        self._running = True
    
    def stop(self):
        """停止Agent"""
        self._running = False
        self.registry.unregister(self.agent_id)


# 便捷函数
def create_collaboration_system() -> tuple:
    """创建协作系统"""
    registry = AgentRegistry()
    message_bus = MessageBus()
    orchestrator = TaskOrchestrator(registry, message_bus)
    
    # 监听结果消息
    def result_handler(msg: AgentMessage):
        if msg.msg_type == MessageType.RESULT:
            orchestrator.handle_result(msg)
    
    message_bus.subscribe("orchestrator", result_handler)
    
    return registry, message_bus, orchestrator


if __name__ == "__main__":
    # 测试代码
    registry, bus, orchestrator = create_collaboration_system()
    
    # 注册测试Agent
    registry.register("finance-agent", AgentRole.SPECIALIST, 
                     ["finance", "stock", "quote"])
    registry.register("research-agent", AgentRole.SPECIALIST,
                     ["research", "analysis", "report"])
    
    print("Agent注册中心:")
    for agent in registry.list_agents():
        print(f"  - {agent['agent_id']}: {agent['capabilities']}")
    
    # 创建任务
    task1 = orchestrator.create_task(
        task_type="finance.quote",
        description="获取茅台股票报价",
        parameters={"symbol": "600519.SH"},
        created_by="user"
    )
    
    print(f"\n创建任务: {task1.task_id}")
    
    # 分配任务
    orchestrator.assign_task(task1.task_id, "finance-agent")
    print(f"任务分配给: finance-agent")
    
    # 模拟结果
    result_msg = AgentMessage(
        msg_type=MessageType.RESULT,
        sender="finance-agent",
        receiver="orchestrator",
        payload={
            "task_id": task1.task_id,
            "result": {"price": 1688.00, "change": 2.5}
        },
        correlation_id=task1.task_id
    )
    bus.publish(result_msg)
    
    print(f"任务状态: {orchestrator.get_task_status(task1.task_id).name}")
    print(f"任务结果: {orchestrator._tasks[task1.task_id].result}")
