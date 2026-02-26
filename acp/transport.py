"""
ACP Transport Layer - 消息传输层实现
支持HTTP和消息队列适配器
"""
import asyncio
import json
from typing import Dict, Optional, Callable, Any
from abc import ABC, abstractmethod
from .core import ACPMessage, ACPAgent


class TransportAdapter(ABC):
    """传输层适配器基类"""
    
    @abstractmethod
    async def send(self, message: ACPMessage, target_endpoint: str) -> bool:
        """发送消息到目标端点"""
        pass
    
    @abstractmethod
    async def start_server(self, handler: Callable[[ACPMessage], Optional[ACPMessage]]):
        """启动服务器接收消息"""
        pass
    
    @abstractmethod
    async def stop(self):
        """停止传输层"""
        pass


class HTTPTransportAdapter(TransportAdapter):
    """HTTP传输适配器"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.server = None
        self._handler: Optional[Callable] = None
    
    async def send(self, message: ACPMessage, target_endpoint: str) -> bool:
        """通过HTTP POST发送消息"""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{target_endpoint}/acp/message"
                async with session.post(
                    url,
                    json=message.to_dict(),
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    return response.status == 200
        except Exception as e:
            print(f"Failed to send message: {e}")
            return False
    
    async def start_server(self, handler: Callable[[ACPMessage], Optional[ACPMessage]]):
        """启动HTTP服务器"""
        from aiohttp import web
        
        self._handler = handler
        
        async def handle_message(request):
            try:
                data = await request.json()
                message = ACPMessage(**data)
                response = handler(message)
                
                if response:
                    return web.json_response(response.to_dict())
                return web.json_response({"status": "ok"})
            except Exception as e:
                return web.json_response({"error": str(e)}, status=400)
        
        async def health(request):
            return web.json_response({"status": "healthy"})
        
        app = web.Application()
        app.router.add_post("/acp/message", handle_message)
        app.router.add_get("/health", health)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        print(f"ACP HTTP server started on {self.host}:{self.port}")
        
        # 保持运行
        while True:
            await asyncio.sleep(3600)
    
    async def stop(self):
        """停止HTTP服务器"""
        pass


class RedisTransportAdapter(TransportAdapter):
    """Redis消息队列适配器"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", channel_prefix: str = "acp"):
        self.redis_url = redis_url
        self.channel_prefix = channel_prefix
        self.redis = None
        self.pubsub = None
        self._handler: Optional[Callable] = None
        self._running = False
    
    async def _get_redis(self):
        """获取Redis连接"""
        if self.redis is None:
            import aioredis
            self.redis = await aioredis.from_url(self.redis_url)
        return self.redis
    
    async def send(self, message: ACPMessage, target_endpoint: str) -> bool:
        """通过Redis发布消息"""
        try:
            redis = await self._get_redis()
            channel = f"{self.channel_prefix}:{target_endpoint}"
            await redis.publish(channel, message.to_json())
            return True
        except Exception as e:
            print(f"Failed to publish message: {e}")
            return False
    
    async def start_server(self, handler: Callable[[ACPMessage], Optional[ACPMessage]]):
        """启动Redis订阅"""
        import aioredis
        
        self._handler = handler
        self._running = True
        
        redis = await self._get_redis()
        self.pubsub = redis.pubsub()
        
        # 订阅所有ACP频道
        await self.pubsub.psubscribe(f"{self.channel_prefix}:*")
        
        print(f"ACP Redis subscriber started on {self.redis_url}")
        
        async for message in self.pubsub.listen():
            if not self._running:
                break
            
            if message["type"] == "pmessage":
                try:
                    data = json.loads(message["data"])
                    acp_message = ACPMessage(**data)
                    handler(acp_message)
                except Exception as e:
                    print(f"Error handling message: {e}")
    
    async def stop(self):
        """停止Redis订阅"""
        self._running = False
        if self.pubsub:
            await self.pubsub.close()


class ACPTransport:
    """ACP传输层管理器"""
    
    def __init__(self, agent: ACPAgent, adapter: TransportAdapter):
        self.agent = agent
        self.adapter = adapter
        self._running = False
    
    def _message_handler(self, message: ACPMessage) -> Optional[ACPMessage]:
        """消息处理入口"""
        return self.agent.handle_message(message)
    
    async def start(self):
        """启动传输层"""
        self._running = True
        await self.adapter.start_server(self._message_handler)
    
    async def stop(self):
        """停止传输层"""
        self._running = False
        await self.adapter.stop()
    
    async def send_to(self, message: ACPMessage, target_endpoint: str) -> bool:
        """发送消息到指定端点"""
        return await self.adapter.send(message, target_endpoint)
    
    async def delegate_task(
        self,
        to_agent_id: str,
        task_type: str,
        payload: Dict,
        priority: str = "normal",
        timeout_ms: int = 60000
    ) -> Optional[Dict]:
        """委托任务给其他Agent"""
        # 查找目标Agent
        target_agent = self.agent.registry.get_agent(to_agent_id)
        if not target_agent:
            print(f"Agent {to_agent_id} not found")
            return None
        
        # 创建任务请求
        message = self.agent.create_task_request(
            to_agent=to_agent_id,
            task_type=task_type,
            payload=payload,
            priority=priority,
            timeout_ms=timeout_ms
        )
        
        # 发送消息
        success = await self.send_to(message, target_agent.endpoint)
        if not success:
            return None
        
        # TODO: 实现异步回调等待结果
        return {"status": "sent", "message_id": message.message_id}


__all__ = [
    "TransportAdapter",
    "HTTPTransportAdapter",
    "RedisTransportAdapter",
    "ACPTransport"
]
