"""
Agent Collaboration Protocol (ACP) - Core Implementation
"""
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import uuid
import asyncio
from abc import ABC, abstractmethod


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


@dataclass
class AgentInfo:
    agent_id: str
    name: str
    capabilities: List[str]
    version: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    type: MessageType
    message_id: str
    from_agent: str
    to_agent: str
    timestamp: datetime
    payload: Dict[str, Any]
    in_reply_to: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "type": self.type.value,
            "message_id": self.message_id,
            "from": self.from_agent,
            "to": self.to_agent,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload,
            "in_reply_to": self.in_reply_to
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Message":
        return cls(
            type=MessageType(data["type"]),
            message_id=data["message_id"],
            from_agent=data["from"],
            to_agent=data["to"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            payload=data["payload"],
            in_reply_to=data.get("in_reply_to")
        )


@dataclass
class TaskRequest:
    task_id: str
    task_type: str
    parameters: Dict[str, Any]
    priority: str = "normal"
    deadline: Optional[datetime] = None


@dataclass
class TaskResponse:
    task_id: str
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None


class MessageBus(ABC):
    """Abstract message bus interface"""
    
    @abstractmethod
    async def send(self, message: Message) -> None:
        pass
    
    @abstractmethod
    async def receive(self, agent_id: str) -> Optional[Message]:
        pass
    
    @abstractmethod
    async def broadcast(self, message: Message) -> None:
        pass


class InMemoryMessageBus(MessageBus):
    """In-memory message bus for single-host multi-agent"""
    
    def __init__(self):
        self.queues: Dict[str, asyncio.Queue] = {}
        self.subscribers: Dict[str, List[Callable]] = {}
    
    async def send(self, message: Message) -> None:
        if message.to_agent not in self.queues:
            self.queues[message.to_agent] = asyncio.Queue()
        await self.queues[message.to_agent].put(message)
    
    async def receive(self, agent_id: str, timeout: float = 30.0) -> Optional[Message]:
        if agent_id not in self.queues:
            self.queues[agent_id] = asyncio.Queue()
        try:
            return await asyncio.wait_for(
                self.queues[agent_id].get(), 
                timeout=timeout
            )
        except asyncio.TimeoutError:
            return None
    
    async def broadcast(self, message: Message) -> None:
        for queue in self.queues.values():
            await queue.put(message)


class Agent:
    """ACP Agent implementation"""
    
    def __init__(
        self, 
        name: str, 
        capabilities: List[str],
        message_bus: Optional[MessageBus] = None,
        version: str = "1.0.0"
    ):
        self.info = AgentInfo(
            agent_id=str(uuid.uuid4()),
            name=name,
            capabilities=capabilities,
            version=version
        )
        self.message_bus = message_bus or InMemoryMessageBus()
        self.handlers: Dict[str, Callable] = {}
        self.pending_tasks: Dict[str, asyncio.Future] = {}
        self.running = False
    
    def handler(self, task_type: str):
        """Decorator to register task handler"""
        def decorator(func: Callable):
            self.handlers[task_type] = func
            return func
        return decorator
    
    async def send_task(
        self, 
        to: str, 
        task_type: str, 
        parameters: Dict[str, Any],
        priority: str = "normal",
        timeout: float = 60.0
    ) -> TaskResponse:
        """Send task request and wait for response"""
        task_id = str(uuid.uuid4())
        
        request = TaskRequest(
            task_id=task_id,
            task_type=task_type,
            parameters=parameters,
            priority=priority
        )
        
        message = Message(
            type=MessageType.TASK_REQUEST,
            message_id=str(uuid.uuid4()),
            from_agent=self.info.agent_id,
            to_agent=to,
            timestamp=datetime.utcnow(),
            payload={
                "task_id": task_id,
                "task_type": task_type,
                "parameters": parameters,
                "priority": priority
            }
        )
        
        # Create future for response
        future = asyncio.get_event_loop().create_future()
        self.pending_tasks[task_id] = future
        
        await self.message_bus.send(message)
        
        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            return TaskResponse(**result)
        except asyncio.TimeoutError:
            return TaskResponse(
                task_id=task_id,
                status=TaskStatus.FAILED,
                error="Task timeout"
            )
        finally:
            self.pending_tasks.pop(task_id, None)
    
    async def _handle_message(self, message: Message) -> None:
        """Process incoming message"""
        if message.type == MessageType.TASK_REQUEST:
            await self._handle_task_request(message)
        elif message.type == MessageType.TASK_RESPONSE:
            await self._handle_task_response(message)
        elif message.type == MessageType.STATUS_UPDATE:
            pass  # Handle status updates
    
    async def _handle_task_request(self, message: Message) -> None:
        """Handle incoming task request"""
        payload = message.payload
        task_type = payload["task_type"]
        task_id = payload["task_id"]
        
        if task_type not in self.handlers:
            response = TaskResponse(
                task_id=task_id,
                status=TaskStatus.FAILED,
                error=f"Unknown task type: {task_type}"
            )
        else:
            handler = self.handlers[task_type]
            request = TaskRequest(**payload)
            
            start_time = datetime.utcnow()
            try:
                result = await handler(request)
                execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                response = TaskResponse(
                    task_id=task_id,
                    status=TaskStatus.COMPLETED,
                    result=result,
                    execution_time_ms=execution_time
                )
            except Exception as e:
                response = TaskResponse(
                    task_id=task_id,
                    status=TaskStatus.FAILED,
                    error=str(e)
                )
        
        # Send response
        response_message = Message(
            type=MessageType.TASK_RESPONSE,
            message_id=str(uuid.uuid4()),
            from_agent=self.info.agent_id,
            to_agent=message.from_agent,
            timestamp=datetime.utcnow(),
            payload={
                "task_id": response.task_id,
                "status": response.status.value,
                "result": response.result,
                "error": response.error,
                "execution_time_ms": response.execution_time_ms
            },
            in_reply_to=message.message_id
        )
        await self.message_bus.send(response_message)
    
    async def _handle_task_response(self, message: Message) -> None:
        """Handle task response"""
        payload = message.payload
        task_id = payload["task_id"]
        
        if task_id in self.pending_tasks:
            future = self.pending_tasks[task_id]
            if not future.done():
                future.set_result(payload)
    
    async def start(self) -> None:
        """Start agent message loop"""
        self.running = True
        while self.running:
            message = await self.message_bus.receive(self.info.agent_id, timeout=1.0)
            if message:
                await self._handle_message(message)
    
    def stop(self) -> None:
        """Stop agent"""
        self.running = False


class Workflow:
    """Workflow orchestration for multi-agent collaboration"""
    
    def __init__(self, name: str):
        self.name = name
        self.steps: List[Dict] = []
        self.agents: Dict[str, Agent] = {}
    
    def add_step(
        self, 
        name: str, 
        agent: str, 
        task_type: str, 
        parameters: Dict[str, Any],
        depends_on: Optional[List[str]] = None
    ):
        """Add workflow step"""
        self.steps.append({
            "name": name,
            "agent": agent,
            "task_type": task_type,
            "parameters": parameters,
            "depends_on": depends_on or [],
            "status": TaskStatus.PENDING
        })
    
    async def execute(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute workflow"""
        results = {}
        context = context or {}
        
        for step in self.steps:
            # Wait for dependencies
            for dep in step["depends_on"]:
                if dep not in results:
                    raise ValueError(f"Dependency {dep} not found")
            
            # Execute step
            agent = self.agents.get(step["agent"])
            if not agent:
                raise ValueError(f"Agent {step['agent']} not found")
            
            # Merge context into parameters
            params = {**step["parameters"], **context}
            
            response = await agent.send_task(
                to=step["agent"],
                task_type=step["task_type"],
                parameters=params
            )
            
            results[step["name"]] = response
            context[f"{step['name']}_result"] = response.result
        
        return results
