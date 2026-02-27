#!/usr/bin/env python3
"""
Agent Collaboration Protocol (ACP) - 核心协议实现
支持多Agent协同工作的标准化通信协议
"""

import asyncio
import json
import uuid
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Callable, Any, Set
from collections import defaultdict
import threading


class MessageType(Enum):
    """消息类型枚举"""
    TASK = "TASK"
    RESULT = "RESULT"
    QUERY = "QUERY"
    RESPONSE = "RESPONSE"
    EVENT = "EVENT"
    HEARTBEAT = "HEARTBEAT"
    ERROR = "ERROR"


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AgentRole(Enum):
    """Agent角色枚举"""
    ORCHESTRATOR = "orchestrator"
    SPECIALIST = "specialist"
    WORKER = "worker"


class WorkflowType(Enum):
    """预定义工作流类型"""
    STOCK_RESEARCH = "stock-research"
    PRODUCT_DEV = "product-dev"


@dataclass
class Message:
    """消息数据结构"""
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    msg_type: MessageType = MessageType.EVENT
    sender: str = ""
    receiver: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)
    correlation_id: str = ""
    priority: int = 5  # 1-10, 1最高
    
    def to_dict(self) -> Dict:
        return {
            "msg_id": self.msg_id,
            "msg_type": self.msg_type.value,
            "sender": self.sender,
            "receiver": self.receiver,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "priority": self.priority
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        return cls(
            msg_id=data.get("msg_id", str(uuid.uuid4())),
            msg_type=MessageType(data.get("msg_type", "EVENT")),
            sender=data.get("sender", ""),
            receiver=data.get("receiver", ""),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            payload=data.get("payload", {}),
            correlation_id=data.get("correlation_id", ""),
            priority=data.get("priority", 5)
        )


@dataclass
class Task:
    """任务数据结构"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str = ""
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: str = ""
    created_by: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    priority: int = 5
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "description": self.description,
            "parameters": self.parameters,
            "status": self.status.value,
            "assigned_to": self.assigned_to,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "error": self.error,
            "dependencies": self.dependencies,
            "priority": self.priority
        }


@dataclass
class AgentInfo:
    """Agent信息数据结构"""
    agent_id: str = ""
    role: AgentRole = AgentRole.SPECIALIST
    capabilities: List[str] = field(default_factory=list)
    status: str = "online"
    last_heartbeat: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "capabilities": self.capabilities,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat,
            "metadata": self.metadata
        }


class MessageBus:
    """消息总线 - 高性能内存消息传递"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._broadcast_subscribers: List[Callable] = []
        self._message_history: List[Message] = []
        self._lock = threading.Lock()
        self._async_queue: Optional[asyncio.Queue] = None
    
    def subscribe(self, agent_id: str, callback: Callable[[Message], None]):
        """订阅特定Agent的消息"""
        with self._lock:
            self._subscribers[agent_id].append(callback)
    
    def subscribe_broadcast(self, callback: Callable[[Message], None]):
        """订阅广播消息"""
        with self._lock:
            self._broadcast_subscribers.append(callback)
    
    def unsubscribe(self, agent_id: str, callback: Callable[[Message], None]):
        """取消订阅"""
        with self._lock:
            if agent_id in self._subscribers:
                if callback in self._subscribers[agent_id]:
                    self._subscribers[agent_id].remove(callback)
    
    def send(self, message: Message) -> bool:
        """发送消息到特定Agent"""
        with self._lock:
            self._message_history.append(message)
            
            # 发送给特定接收者
            if message.receiver and message.receiver in self._subscribers:
                for callback in self._subscribers[message.receiver]:
                    try:
                        callback(message)
                    except Exception as e:
                        print(f"Error delivering message to {message.receiver}: {e}")
                return True
            
            # 广播消息
            if not message.receiver or message.receiver == "*":
                for callback in self._broadcast_subscribers:
                    try:
                        callback(message)
                    except Exception as e:
                        print(f"Error in broadcast: {e}")
                return True
        
        return False
    
    def broadcast(self, message: Message) -> bool:
        """广播消息给所有订阅者"""
        message.receiver = "*"
        return self.send(message)
    
    def get_message_history(self, limit: int = 100) -> List[Message]:
        """获取消息历史"""
        with self._lock:
            return self._message_history[-limit:]
    
    def clear_history(self):
        """清空消息历史"""
        with self._lock:
            self._message_history.clear()


class AgentRegistry:
    """Agent注册中心 - 动态发现和管理Agent"""
    
    def __init__(self, message_bus: MessageBus):
        self._agents: Dict[str, AgentInfo] = {}
        self._message_bus = message_bus
        self._lock = threading.Lock()
        self._heartbeat_timeout = 60  # 秒
    
    def register(self, agent_info: AgentInfo) -> bool:
        """注册Agent"""
        with self._lock:
            agent_info.last_heartbeat = datetime.now().isoformat()
            self._agents[agent_info.agent_id] = agent_info
            
            # 广播注册事件
            self._message_bus.broadcast(Message(
                msg_type=MessageType.EVENT,
                sender="registry",
                payload={
                    "event": "agent_registered",
                    "agent_id": agent_info.agent_id,
                    "role": agent_info.role.value,
                    "capabilities": agent_info.capabilities
                }
            ))
            return True
    
    def unregister(self, agent_id: str) -> bool:
        """注销Agent"""
        with self._lock:
            if agent_id in self._agents:
                del self._agents[agent_id]
                
                # 广播注销事件
                self._message_bus.broadcast(Message(
                    msg_type=MessageType.EVENT,
                    sender="registry",
                    payload={
                        "event": "agent_unregistered",
                        "agent_id": agent_id
                    }
                ))
                return True
            return False
    
    def heartbeat(self, agent_id: str) -> bool:
        """更新Agent心跳"""
        with self._lock:
            if agent_id in self._agents:
                self._agents[agent_id].last_heartbeat = datetime.now().isoformat()
                self._agents[agent_id].status = "online"
                return True
            return False
    
    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """获取Agent信息"""
        with self._lock:
            return self._agents.get(agent_id)
    
    def list_agents(self) -> List[AgentInfo]:
        """列出所有Agent"""
        with self._lock:
            return list(self._agents.values())
    
    def find_by_capability(self, capability: str) -> List[AgentInfo]:
        """按能力查找Agent"""
        with self._lock:
            return [
                agent for agent in self._agents.values()
                if capability in agent.capabilities
            ]
    
    def find_by_role(self, role: AgentRole) -> List[AgentInfo]:
        """按角色查找Agent"""
        with self._lock:
            return [
                agent for agent in self._agents.values()
                if agent.role == role
            ]
    
    def check_health(self) -> Dict[str, List[str]]:
        """检查Agent健康状态"""
        with self._lock:
            now = datetime.now()
            healthy = []
            unhealthy = []
            
            for agent_id, agent in self._agents.items():
                last_hb = datetime.fromisoformat(agent.last_heartbeat)
                if (now - last_hb).seconds < self._heartbeat_timeout:
                    healthy.append(agent_id)
                else:
                    unhealthy.append(agent_id)
                    agent.status = "offline"
            
            return {"healthy": healthy, "unhealthy": unhealthy}


class TaskOrchestrator:
    """任务编排器 - 支持顺序/并行/条件执行的任务编排"""
    
    def __init__(self, registry: AgentRegistry, message_bus: MessageBus):
        self._tasks: Dict[str, Task] = {}
        self._registry = registry
        self._message_bus = message_bus
        self._lock = threading.Lock()
        self._callbacks: Dict[str, List[Callable]] = defaultdict(list)
    
    def create_task(
        self,
        task_type: str,
        description: str,
        parameters: Dict[str, Any] = None,
        created_by: str = "",
        dependencies: List[str] = None,
        priority: int = 5
    ) -> Task:
        """创建新任务"""
        task = Task(
            task_type=task_type,
            description=description,
            parameters=parameters or {},
            created_by=created_by,
            dependencies=dependencies or [],
            priority=priority
        )
        
        with self._lock:
            self._tasks[task.task_id] = task
        
        # 广播任务创建事件
        self._message_bus.broadcast(Message(
            msg_type=MessageType.EVENT,
            sender="orchestrator",
            payload={
                "event": "task_created",
                "task_id": task.task_id,
                "task_type": task_type,
                "description": description
            }
        ))
        
        return task
    
    def assign_task(self, task_id: str, agent_id: str) -> bool:
        """分配任务给Agent"""
        with self._lock:
            if task_id not in self._tasks:
                return False
            
            task = self._tasks[task_id]
            
            # 检查依赖是否完成
            for dep_id in task.dependencies:
                if dep_id in self._tasks:
                    dep_task = self._tasks[dep_id]
                    if dep_task.status != TaskStatus.COMPLETED:
                        return False
            
            task.assigned_to = agent_id
            task.status = TaskStatus.ASSIGNED
        
        # 发送任务消息
        self._message_bus.send(Message(
            msg_type=MessageType.TASK,
            sender="orchestrator",
            receiver=agent_id,
            correlation_id=task_id,
            payload={
                "task_id": task_id,
                "task_type": task.task_type,
                "description": task.description,
                "parameters": task.parameters
            }
        ))
        
        return True
    
    def start_task(self, task_id: str) -> bool:
        """标记任务开始执行"""
        with self._lock:
            if task_id not in self._tasks:
                return False
            
            task = self._tasks[task_id]
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now().isoformat()
        
        self._message_bus.broadcast(Message(
            msg_type=MessageType.EVENT,
            sender="orchestrator",
            payload={
                "event": "task_started",
                "task_id": task_id
            }
        ))
        
        return True
    
    def complete_task(self, task_id: str, result: Dict[str, Any]) -> bool:
        """完成任务"""
        with self._lock:
            if task_id not in self._tasks:
                return False
            
            task = self._tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            task.result = result
        
        # 触发回调
        for callback in self._callbacks.get(task_id, []):
            try:
                callback(task)
            except Exception as e:
                print(f"Error in task callback: {e}")
        
        self._message_bus.broadcast(Message(
            msg_type=MessageType.EVENT,
            sender="orchestrator",
            payload={
                "event": "task_completed",
                "task_id": task_id,
                "result": result
            }
        ))
        
        return True
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """标记任务失败"""
        with self._lock:
            if task_id not in self._tasks:
                return False
            
            task = self._tasks[task_id]
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now().isoformat()
            task.error = error
        
        self._message_bus.broadcast(Message(
            msg_type=MessageType.EVENT,
            sender="orchestrator",
            payload={
                "event": "task_failed",
                "task_id": task_id,
                "error": error
            }
        ))
        
        return True
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务信息"""
        with self._lock:
            return self._tasks.get(task_id)
    
    def list_tasks(self, status: TaskStatus = None) -> List[Task]:
        """列出任务"""
        with self._lock:
            if status:
                return [t for t in self._tasks.values() if t.status == status]
            return list(self._tasks.values())
    
    def on_task_complete(self, task_id: str, callback: Callable[[Task], None]):
        """注册任务完成回调"""
        with self._lock:
            self._callbacks[task_id].append(callback)
    
    def auto_assign(self, task_id: str) -> Optional[str]:
        """自动分配任务给合适的Agent"""
        with self._lock:
            if task_id not in self._tasks:
                return None
            
            task = self._tasks[task_id]
            
            # 根据任务类型查找Agent
            capability_map = {
                "finance": ["finance-pro"],
                "coding": ["coding-pro"],
                "product": ["product-pro"],
                "research": ["research-pro"]
            }
            
            for prefix, agents in capability_map.items():
                if task.task_type.startswith(prefix):
                    for agent_id in agents:
                        agent = self._registry.get_agent(agent_id)
                        if agent and agent.status == "online":
                            self.assign_task(task_id, agent_id)
                            return agent_id
            
            return None


class ResultAggregator:
    """结果聚合器 - 智能合并多Agent结果"""
    
    def __init__(self):
        self._results: Dict[str, List[Dict]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def add_result(self, correlation_id: str, agent_id: str, result: Dict[str, Any]):
        """添加结果"""
        with self._lock:
            self._results[correlation_id].append({
                "agent_id": agent_id,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
    
    def get_results(self, correlation_id: str) -> List[Dict]:
        """获取所有结果"""
        with self._lock:
            return self._results.get(correlation_id, [])
    
    def aggregate(self, correlation_id: str, strategy: str = "merge") -> Dict[str, Any]:
        """聚合结果"""
        with self._lock:
            results = self._results.get(correlation_id, [])
        
        if not results:
            return {"status": "no_results"}
        
        if strategy == "merge":
            # 合并所有结果
            merged = {}
            for r in results:
                merged.update(r["result"])
            return {"status": "success", "data": merged, "sources": [r["agent_id"] for r in results]}
        
        elif strategy == "vote":
            # 投票策略（用于冲突解决）
            return {"status": "success", "results": results, "strategy": "vote"}
        
        elif strategy == "priority":
            # 按优先级选择
            return results[0]["result"] if results else {}
        
        return {"status": "unknown_strategy"}
    
    def resolve_conflict(self, correlation_id: str, resolution: str = "latest") -> Dict[str, Any]:
        """解决冲突"""
        results = self.get_results(correlation_id)
        
        if not results:
            return {}
        
        if resolution == "latest":
            # 选择最新的结果
            sorted_results = sorted(results, key=lambda x: x["timestamp"], reverse=True)
            return sorted_results[0]["result"]
        
        elif resolution == "consensus":
            # 简单多数共识
            return self._find_consensus(results)
        
        return results[0]["result"]
    
    def _find_consensus(self, results: List[Dict]) -> Dict[str, Any]:
        """查找共识"""
        if not results:
            return {}
        
        # 简单的键值共识检测
        consensus = {}
        key_votes = defaultdict(lambda: defaultdict(int))
        
        for r in results:
            for key, value in r["result"].items():
                key_votes[key][str(value)] += 1
        
        for key, votes in key_votes.items():
            most_common = max(votes.items(), key=lambda x: x[1])
            consensus[key] = most_common[0]
        
        return consensus


class CollaborationAgent(ABC):
    """协作Agent基类"""
    
    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        capabilities: List[str],
        registry: AgentRegistry,
        message_bus: MessageBus
    ):
        self.agent_id = agent_id
        self.role = role
        self.capabilities = capabilities
        self._registry = registry
        self._message_bus = message_bus
        self._running = False
        self._heartbeat_task = None
        
        # 注册到消息总线
        self._message_bus.subscribe(agent_id, self._on_message)
        
        # 注册到注册中心
        self._registry.register(AgentInfo(
            agent_id=agent_id,
            role=role,
            capabilities=capabilities
        ))
    
    def _on_message(self, message: Message):
        """处理接收到的消息"""
        if message.msg_type == MessageType.TASK:
            self._handle_task(message)
        elif message.msg_type == MessageType.QUERY:
            self._handle_query(message)
        elif message.msg_type == MessageType.HEARTBEAT:
            self._registry.heartbeat(self.agent_id)
    
    @abstractmethod
    def _handle_task(self, message: Message):
        """处理任务消息（子类必须实现）"""
        pass
    
    @abstractmethod
    def _handle_query(self, message: Message):
        """处理查询消息（子类必须实现）"""
        pass
    
    def send_result(self, task_id: str, result: Dict[str, Any]):
        """发送任务结果"""
        self._message_bus.send(Message(
            msg_type=MessageType.RESULT,
            sender=self.agent_id,
            receiver="orchestrator",
            correlation_id=task_id,
            payload={"task_id": task_id, "result": result}
        ))
    
    def send_error(self, task_id: str, error: str):
        """发送错误"""
        self._message_bus.send(Message(
            msg_type=MessageType.ERROR,
            sender=self.agent_id,
            receiver="orchestrator",
            correlation_id=task_id,
            payload={"task_id": task_id, "error": error}
        ))
    
    def query(self, target_agent: str, query_type: str, parameters: Dict[str, Any]) -> str:
        """向其他Agent发送查询"""
        query_id = str(uuid.uuid4())
        self._message_bus.send(Message(
            msg_type=MessageType.QUERY,
            sender=self.agent_id,
            receiver=target_agent,
            correlation_id=query_id,
            payload={"query_type": query_type, "parameters": parameters}
        ))
        return query_id
    
    def start(self):
        """启动Agent"""
        self._running = True
        self._start_heartbeat()
    
    def stop(self):
        """停止Agent"""
        self._running = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
    
    def _start_heartbeat(self):
        """启动心跳"""
        def heartbeat_loop():
            while self._running:
                self._registry.heartbeat(self.agent_id)
                time.sleep(30)  # 每30秒发送一次心跳
        
        self._heartbeat_task = threading.Thread(target=heartbeat_loop, daemon=True)
        self._heartbeat_task.start()


class MasterOrchestratorAgent(CollaborationAgent):
    """主编排Agent - 协调其他Agent工作"""
    
    def __init__(self, registry: AgentRegistry, message_bus: MessageBus, orchestrator: TaskOrchestrator):
        super().__init__(
            agent_id="master-orchestrator",
            role=AgentRole.ORCHESTRATOR,
            capabilities=["orchestrate", "coordinate", "plan", "workflow"],
            registry=registry,
            message_bus=message_bus
        )
        self._orchestrator = orchestrator
        self._workflows: Dict[str, Dict] = {}
    
    def _handle_task(self, message: Message):
        """处理任务"""
        payload = message.payload
        task_type = payload.get("task_type")
        
        if task_type == "workflow.execute":
            workflow_type = payload.get("parameters", {}).get("workflow_type")
            if workflow_type == WorkflowType.STOCK_RESEARCH.value:
                self._execute_stock_research_workflow(payload)
            elif workflow_type == WorkflowType.PRODUCT_DEV.value:
                self._execute_product_dev_workflow(payload)
    
    def _handle_query(self, message: Message):
        """处理查询"""
        payload = message.payload
        query_type = payload.get("query_type")
        
        if query_type == "workflow.status":
            workflow_id = payload.get("parameters", {}).get("workflow_id")
            status = self.get_workflow_status(workflow_id)
            
            self._message_bus.send(Message(
                msg_type=MessageType.RESPONSE,
                sender=self.agent_id,
                receiver=message.sender,
                correlation_id=message.correlation_id,
                payload={"workflow_id": workflow_id, "status": status}
            ))
    
    def create_stock_research_workflow(self, symbol: str) -> str:
        """创建股票研究工作流"""
        workflow_id = str(uuid.uuid4())
        
        # 创建任务
        task1 = self._orchestrator.create_task(
            task_type="finance.quote",
            description=f"获取股票 {symbol} 的实时行情",
            parameters={"symbol": symbol},
            created_by=self.agent_id
        )
        
        task2 = self._orchestrator.create_task(
            task_type="research.search",
            description=f"研究 {symbol} 公司背景",
            parameters={"query": f"{symbol} 公司简介 主营业务"},
            created_by=self.agent_id,
            dependencies=[task1.task_id]
        )
        
        task3 = self._orchestrator.create_task(
            task_type="research.deep",
            description=f"深度分析 {symbol}",
            parameters={"topic": f"{symbol} 投资价值分析"},
            created_by=self.agent_id,
            dependencies=[task2.task_id]
        )
        
        # 自动分配任务
        self._orchestrator.auto_assign(task1.task_id)
        self._orchestrator.auto_assign(task2.task_id)
        self._orchestrator.auto_assign(task3.task_id)
        
        self._workflows[workflow_id] = {
            "type": WorkflowType.STOCK_RESEARCH.value,
            "symbol": symbol,
            "tasks": [task1.task_id, task2.task_id, task3.task_id],
            "status": "running"
        }
        
        return workflow_id
    
    def create_product_dev_workflow(self, product_name: str) -> str:
        """创建产品开发工作流"""
        workflow_id = str(uuid.uuid4())
        
        task1 = self._orchestrator.create_task(
            task_type="research.search",
            description=f"{product_name} 市场调研",
            parameters={"query": f"{product_name} 市场规模 竞品分析"},
            created_by=self.agent_id
        )
        
        task2 = self._orchestrator.create_task(
            task_type="product.competitor",
            description=f"{product_name} 竞品分析",
            parameters={"product": product_name},
            created_by=self.agent_id,
            dependencies=[task1.task_id]
        )
        
        task3 = self._orchestrator.create_task(
            task_type="product.prd",
            description=f"生成 {product_name} PRD",
            parameters={"feature": product_name},
            created_by=self.agent_id,
            dependencies=[task2.task_id]
        )
        
        task4 = self._orchestrator.create_task(
            task_type="coding.generate",
            description=f"生成 {product_name} 原型代码",
            parameters={"prompt": f"创建 {product_name} 的MVP原型"},
            created_by=self.agent_id,
            dependencies=[task3.task_id]
        )
        
        # 自动分配
        for task in [task1, task2, task3, task4]:
            self._orchestrator.auto_assign(task.task_id)
        
        self._workflows[workflow_id] = {
            "type": WorkflowType.PRODUCT_DEV.value,
            "product": product_name,
            "tasks": [task1.task_id, task2.task_id, task3.task_id, task4.task_id],
            "status": "running"
        }
        
        return workflow_id
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """获取工作流状态"""
        if workflow_id not in self._workflows:
            return {"error": "Workflow not found"}
        
        workflow = self._workflows[workflow_id]
        task_statuses = []
        
        for task_id in workflow["tasks"]:
            task = self._orchestrator.get_task(task_id)
            if task:
                task_statuses.append({
                    "task_id": task_id,
                    "status": task.status.value,
                    "assigned_to": task.assigned_to
                })
        
        # 检查是否全部完成
        all_completed = all(
            s["status"] == TaskStatus.COMPLETED.value 
            for s in task_statuses
        )
        
        if all_completed:
            workflow["status"] = "completed"
        
        return {
            "workflow_id": workflow_id,
            "type": workflow["type"],
            "status": workflow["status"],
            "tasks": task_statuses
        }
    
    def _execute_stock_research_workflow(self, payload: Dict):
        """执行股票研究工作流"""
        symbol = payload.get("parameters", {}).get("symbol")
        if symbol:
            workflow_id = self.create_stock_research_workflow(symbol)
            self.send_result(payload.get("task_id"), {"workflow_id": workflow_id})
    
    def _execute_product_dev_workflow(self, payload: Dict):
        """执行产品开发工作流"""
        product = payload.get("parameters", {}).get("product")
        if product:
            workflow_id = self.create_product_dev_workflow(product)
            self.send_result(payload.get("task_id"), {"workflow_id": workflow_id})


def create_collaboration_system() -> tuple:
    """创建完整的协作系统"""
    # 创建基础设施
    message_bus = MessageBus()
    registry = AgentRegistry(message_bus)
    orchestrator = TaskOrchestrator(registry, message_bus)
    aggregator = ResultAggregator()
    
    # 创建主编排Agent
    master = MasterOrchestratorAgent(registry, message_bus, orchestrator)
    master.start()
    
    return master, registry, message_bus, orchestrator, aggregator


if __name__ == "__main__":
    # 测试代码
    master, registry, bus, orchestrator, aggregator = create_collaboration_system()
    
    print("=== Agent Collaboration Protocol Test ===")
    print(f"\nRegistered agents: {len(registry.list_agents())}")
    
    # 创建工作流
    workflow_id = master.create_stock_research_workflow("600519.SH")
    print(f"\nCreated workflow: {workflow_id}")
    
    # 检查状态
    status = master.get_workflow_status(workflow_id)
    print(f"\nWorkflow status: {json.dumps(status, indent=2, default=str)}")
    
    print("\n=== Test Complete ===")
