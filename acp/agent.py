"""
Agent Collaboration Protocol (ACP) - Agent基类
"""
import asyncio
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, TypeVar, Generic
from dataclasses import dataclass

from .message import (
    Message, MessageType, AgentInfo, TaskRequest, TaskResponse,
    TaskStatus, Priority, create_task_request_message,
    create_task_response_message, create_status_update_message,
    create_discovery_message
)
from .message_bus import MessageBus, InMemoryMessageBus


T = TypeVar('T')


@dataclass
class Task:
    """任务包装器"""
    request: TaskRequest
    response_future: asyncio.Future
    start_time: datetime
    

class Agent:
    """ACP Agent基类"""
    
    def __init__(
        self,
        name: str,
        capabilities: List[str],
        version: str = "1.0.0",
        message_bus: Optional[MessageBus] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = str(uuid.uuid4())
        self.name = name
        self.capabilities = capabilities
        self.version = version
        self.metadata = metadata or {}
        
        self._message_bus = message_bus or InMemoryMessageBus()
        self._handlers: Dict[str, Callable[[TaskRequest], Any]] = {}
        self._pending_tasks: Dict[str, Task] = {}
        self._running = False
        self._task_queue: asyncio.Queue = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None
        
        # 统计信息
        self._stats = {
            "tasks_received": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "messages_sent": 0,
            "messages_received": 0
        }
    
    @property
    def info(self) -> AgentInfo:
        """获取Agent信息"""
        return AgentInfo(
            agent_id=self.agent_id,
            name=self.name,
            capabilities=self.capabilities,
            version=self.version,
            metadata=self.metadata
        )
    
    def handler(self, task_type: str) -> Callable:
        """装饰器：注册任务处理器"""
        def decorator(func: Callable[[TaskRequest], Any]) -> Callable[[TaskRequest], Any]:
            self._handlers[task_type] = func
            return func
        return decorator
    
    async def start(self) -> None:
        """启动Agent"""
        if self._running:
            return
        
        self._running = True
        
        # 订阅消息总线
        await self._message_bus.subscribe(self.agent_id, self._on_message)
        
        # 启动工作线程
        self._worker_task = asyncio.create_task(self._worker())
        
        # 发送发现消息
        await self._send_discovery()
        
        print(f"Agent '{self.name}' ({self.agent_id}) started")
    
    async def stop(self) -> None:
        """停止Agent"""
        if not self._running:
            return
        
        self._running = False
        
        # 取消工作线程
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        
        # 取消订阅
        await self._message_bus.unsubscribe(self.agent_id)
        
        # 清理待处理任务
        for task in self._pending_tasks.values():
            if not task.response_future.done():
                task.response_future.cancel()
        self._pending_tasks.clear()
        
        print(f"Agent '{self.name}' stopped")
    
    async def _worker(self) -> None:
        """工作线程 - 处理任务队列"""
        while self._running:
            try:
                task_request = await asyncio.wait_for(
                    self._task_queue.get(),
                    timeout=1.0
                )
                await self._process_task(task_request)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in worker: {e}")
    
    async def _process_task(self, request: TaskRequest) -> None:
        """处理任务"""
        handler = self._handlers.get(request.task_type)
        
        if not handler:
            print(f"No handler for task type: {request.task_type}")
            return
        
        try:
            # 发送状态更新 - 开始
            await self._send_status_update(request.task_id, TaskStatus.IN_PROGRESS, 0.0, "Starting...")
            
            # 执行任务
            if asyncio.iscoroutinefunction(handler):
                result = await handler(request)
            else:
                result = handler(request)
            
            # 发送状态更新 - 完成
            await self._send_status_update(request.task_id, TaskStatus.COMPLETED, 1.0, "Completed")
            
            self._stats["tasks_completed"] += 1
            
        except Exception as e:
            print(f"Error processing task {request.task_id}: {e}")
            await self._send_status_update(request.task_id, TaskStatus.FAILED, 0.0, str(e))
            self._stats["tasks_failed"] += 1
    
    async def _on_message(self, message: Message) -> None:
        """处理接收到的消息"""
        self._stats["messages_received"] += 1
        
        if message.msg_type == MessageType.TASK_REQUEST:
            await self._handle_task_request(message)
        elif message.msg_type == MessageType.TASK_RESPONSE:
            await self._handle_task_response(message)
        elif message.msg_type == MessageType.STATUS_UPDATE:
            await self._handle_status_update(message)
        elif message.msg_type == MessageType.DISCOVERY:
            await self._handle_discovery(message)
    
    async def _handle_task_request(self, message: Message) -> None:
        """处理任务请求"""
        task_request = TaskRequest.from_dict(message.payload)
        self._stats["tasks_received"] += 1
        
        # 检查是否有处理器
        if task_request.task_type not in self._handlers:
            # 发送失败响应
            response = create_task_response_message(
                from_agent=self.agent_id,
                to_agent=message.from_agent,
                in_reply_to=message.message_id,
                task_id=task_request.task_id,
                status=TaskStatus.FAILED,
                error=f"Task type '{task_request.task_type}' not supported"
            )
            await self._message_bus.publish(response)
            self._stats["messages_sent"] += 1
            return
        
        # 添加到任务队列
        await self._task_queue.put(task_request)
        
        # 发送确认
        await self._send_status_update(
            task_request.task_id,
            TaskStatus.PENDING,
            0.0,
            "Task queued"
        )
    
    async def _handle_task_response(self, message: Message) -> None:
        """处理任务响应"""
        task_response = TaskResponse.from_dict(message.payload)
        
        # 查找对应的待处理任务
        task = self._pending_tasks.get(task_response.task_id)
        if task and not task.response_future.done():
            task.response_future.set_result(task_response)
            del self._pending_tasks[task_response.task_id]
    
    async def _handle_status_update(self, message: Message) -> None:
        """处理状态更新（可由子类覆盖）"""
        pass
    
    async def _handle_discovery(self, message: Message) -> None:
        """处理发现消息（可由子类覆盖）"""
        pass
    
    async def send_task(
        self,
        to_agent: str,
        task_type: str,
        parameters: Dict[str, Any],
        priority: Priority = Priority.MEDIUM,
        timeout: float = 30.0
    ) -> TaskResponse:
        """
        发送任务并等待响应
        
        Args:
            to_agent: 目标Agent ID
            task_type: 任务类型
            parameters: 任务参数
            priority: 优先级
            timeout: 超时时间（秒）
        
        Returns:
            TaskResponse
        """
        task_id = str(uuid.uuid4())
        
        # 创建任务请求消息
        message = create_task_request_message(
            from_agent=self.agent_id,
            to_agent=to_agent,
            task_type=task_type,
            parameters=parameters,
            priority=priority
        )
        
        # 创建响应Future
        response_future = asyncio.get_event_loop().create_future()
        
        # 记录待处理任务
        task_request = TaskRequest.from_dict(message.payload)
        self._pending_tasks[task_request.task_id] = Task(
            request=task_request,
            response_future=response_future,
            start_time=datetime.utcnow()
        )
        
        # 发送消息
        await self._message_bus.publish(message)
        self._stats["messages_sent"] += 1
        
        # 等待响应
        try:
            response = await asyncio.wait_for(response_future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            del self._pending_tasks[task_request.task_id]
            return TaskResponse(
                task_id=task_id,
                status=TaskStatus.FAILED,
                error=f"Timeout after {timeout}s"
            )
    
    async def send_response(
        self,
        to_agent: str,
        in_reply_to: str,
        task_id: str,
        status: TaskStatus,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> None:
        """发送任务响应"""
        message = create_task_response_message(
            from_agent=self.agent_id,
            to_agent=to_agent,
            in_reply_to=in_reply_to,
            task_id=task_id,
            status=status,
            result=result,
            error=error
        )
        await self._message_bus.publish(message)
        self._stats["messages_sent"] += 1
    
    async def _send_status_update(
        self,
        task_id: str,
        status: TaskStatus,
        progress: float,
        message: str
    ) -> None:
        """发送状态更新"""
        msg = create_status_update_message(
            from_agent=self.agent_id,
            to_agent="broadcast",  # 状态更新广播
            task_id=task_id,
            status=status,
            progress=progress,
            message=message
        )
        await self._message_bus.publish(msg)
        self._stats["messages_sent"] += 1
    
    async def _send_discovery(self) -> None:
        """发送发现消息"""
        message = create_discovery_message(
            from_agent=self.agent_id,
            agent_info=self.info,
            action="register"
        )
        await self._message_bus.publish(message)
        self._stats["messages_sent"] += 1
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return self._stats.copy()
