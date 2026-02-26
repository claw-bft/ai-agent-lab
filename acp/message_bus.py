"""
Agent Collaboration Protocol (ACP) - Message Bus
支持In-Memory和Redis两种后端
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional, Set
from collections import defaultdict

from .message import Message, MessageType


class MessageBus(ABC):
    """消息总线抽象基类"""
    
    @abstractmethod
    async def publish(self, message: Message) -> None:
        """发布消息"""
        pass
    
    @abstractmethod
    async def subscribe(self, agent_id: str, callback: Callable[[Message], None]) -> None:
        """订阅消息"""
        pass
    
    @abstractmethod
    async def unsubscribe(self, agent_id: str) -> None:
        """取消订阅"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """关闭连接"""
        pass


class InMemoryMessageBus(MessageBus):
    """内存消息总线 - 适用于单机多Agent场景"""
    
    def __init__(self):
        self._subscribers: Dict[str, Callable[[Message], None]] = {}
        self._broadcast_handlers: Set[Callable[[Message], None]] = set()
        self._message_history: List[Message] = []
        self._max_history = 1000
    
    async def publish(self, message: Message) -> None:
        """发布消息到总线"""
        self._message_history.append(message)
        
        # 限制历史记录大小
        if len(self._message_history) > self._max_history:
            self._message_history = self._message_history[-self._max_history:]
        
        # 发送给特定接收者
        if message.to_agent != "broadcast":
            if message.to_agent in self._subscribers:
                try:
                    await self._notify(self._subscribers[message.to_agent], message)
                except Exception as e:
                    print(f"Error notifying subscriber {message.to_agent}: {e}")
        else:
            # 广播消息
            for agent_id, callback in self._subscribers.items():
                if agent_id != message.from_agent:  # 不发送给自己
                    try:
                        await self._notify(callback, message)
                    except Exception as e:
                        print(f"Error broadcasting to {agent_id}: {e}")
    
    async def _notify(self, callback: Callable[[Message], None], message: Message) -> None:
        """异步通知订阅者"""
        if asyncio.iscoroutinefunction(callback):
            await callback(message)
        else:
            callback(message)
    
    async def subscribe(self, agent_id: str, callback: Callable[[Message], None]) -> None:
        """订阅消息"""
        self._subscribers[agent_id] = callback
    
    async def unsubscribe(self, agent_id: str) -> None:
        """取消订阅"""
        if agent_id in self._subscribers:
            del self._subscribers[agent_id]
    
    async def close(self) -> None:
        """关闭总线"""
        self._subscribers.clear()
        self._broadcast_handlers.clear()
    
    def get_message_history(self, limit: int = 100) -> List[Message]:
        """获取消息历史"""
        return self._message_history[-limit:]
    
    def get_subscribers(self) -> List[str]:
        """获取所有订阅者"""
        return list(self._subscribers.keys())


class RedisMessageBus(MessageBus):
    """Redis消息总线 - 适用于分布式部署"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", channel_prefix: str = "acp"):
        self.redis_url = redis_url
        self.channel_prefix = channel_prefix
        self._redis = None
        self._pubsub = None
        self._subscribers: Dict[str, Callable[[Message], None]] = {}
        self._running = False
        self._listener_task = None
        
        try:
            import redis.asyncio as redis
            self._redis_module = redis
        except ImportError:
            raise ImportError("Redis support requires 'redis' package. Install with: pip install redis")
    
    async def connect(self) -> None:
        """连接到Redis"""
        self._redis = await self._redis_module.from_url(self.redis_url)
        self._pubsub = self._redis.pubsub()
        self._running = True
        self._listener_task = asyncio.create_task(self._listen())
    
    async def _listen(self) -> None:
        """监听Redis消息"""
        async for message in self._pubsub.listen():
            if not self._running:
                break
            if message["type"] == "message":
                try:
                    import json
                    data = json.loads(message["data"])
                    msg = Message.from_dict(data)
                    
                    # 分发给本地订阅者
                    if msg.to_agent in self._subscribers:
                        await self._notify(self._subscribers[msg.to_agent], msg)
                    elif msg.to_agent == "broadcast":
                        for agent_id, callback in self._subscribers.items():
                            if agent_id != msg.from_agent:
                                await self._notify(callback, msg)
                except Exception as e:
                    print(f"Error processing Redis message: {e}")
    
    async def _notify(self, callback: Callable[[Message], None], message: Message) -> None:
        """异步通知订阅者"""
        if asyncio.iscoroutinefunction(callback):
            await callback(message)
        else:
            callback(message)
    
    async def publish(self, message: Message) -> None:
        """发布消息到Redis"""
        if not self._redis:
            raise RuntimeError("Redis connection not established. Call connect() first.")
        
        import json
        channel = f"{self.channel_prefix}:broadcast"
        await self._redis.publish(channel, json.dumps(message.to_dict()))
    
    async def subscribe(self, agent_id: str, callback: Callable[[Message], None]) -> None:
        """订阅消息"""
        if not self._pubsub:
            raise RuntimeError("Redis connection not established. Call connect() first.")
        
        self._subscribers[agent_id] = callback
        channel = f"{self.channel_prefix}:broadcast"
        await self._pubsub.subscribe(channel)
    
    async def unsubscribe(self, agent_id: str) -> None:
        """取消订阅"""
        if agent_id in self._subscribers:
            del self._subscribers[agent_id]
        
        # 如果没有订阅者了，取消订阅频道
        if not self._subscribers and self._pubsub:
            channel = f"{self.channel_prefix}:broadcast"
            await self._pubsub.unsubscribe(channel)
    
    async def close(self) -> None:
        """关闭Redis连接"""
        self._running = False
        
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        
        if self._pubsub:
            await self._pubsub.close()
        
        if self._redis:
            await self._redis.close()
        
        self._subscribers.clear()


class MessageBusFactory:
    """消息总线工厂"""
    
    @staticmethod
    def create(backend: str = "memory", **kwargs) -> MessageBus:
        """
        创建消息总线实例
        
        Args:
            backend: "memory" 或 "redis"
            **kwargs: 传递给具体实现的参数
        
        Returns:
            MessageBus实例
        """
        if backend == "memory":
            return InMemoryMessageBus()
        elif backend == "redis":
            bus = RedisMessageBus(**kwargs)
            return bus
        else:
            raise ValueError(f"Unknown backend: {backend}. Supported: memory, redis")
