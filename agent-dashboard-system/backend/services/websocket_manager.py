from fastapi import WebSocket
from typing import Dict, Set, List
import asyncio
import json

class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self._connections: Set[WebSocket] = set()
        self._subscriptions: Dict[WebSocket, Set[str]] = {}  # 会话订阅
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket):
        """接受新连接"""
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)
            self._subscriptions[websocket] = set()
        print(f"[WS] Client connected. Total: {len(self._connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """断开连接"""
        if websocket in self._connections:
            self._connections.remove(websocket)
        if websocket in self._subscriptions:
            del self._subscriptions[websocket]
        print(f"[WS] Client disconnected. Total: {len(self._connections)}")
    
    def subscribe(self, websocket: WebSocket, session_id: str):
        """订阅特定会话更新"""
        if websocket in self._subscriptions:
            self._subscriptions[websocket].add(session_id)
    
    def unsubscribe(self, websocket: WebSocket, session_id: str):
        """取消订阅"""
        if websocket in self._subscriptions:
            self._subscriptions[websocket].discard(session_id)
    
    async def broadcast(self, message: dict):
        """广播消息给所有客户端"""
        if not self._connections:
            return
        
        disconnected = set()
        
        for ws in self._connections:
            try:
                await ws.send_json(message)
            except Exception as e:
                print(f"[WS] Send error: {e}")
                disconnected.add(ws)
        
        # 清理断开的连接
        for ws in disconnected:
            self.disconnect(ws)
    
    async def send_to_session_subscribers(self, session_id: str, message: dict):
        """发送给订阅了特定会话的客户端"""
        for ws, subs in self._subscriptions.items():
            if session_id in subs and ws in self._connections:
                try:
                    await ws.send_json(message)
                except:
                    pass
    
    def get_connection_count(self) -> int:
        """获取连接数"""
        return len(self._connections)
