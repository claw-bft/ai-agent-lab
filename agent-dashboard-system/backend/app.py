from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Set
import sqlite3
import os

from services.session_scanner import SessionScanner
from services.data_store import DataStore
from services.websocket_manager import WebSocketManager

# Global instances
data_store: DataStore = None
scanner: SessionScanner = None
ws_manager: WebSocketManager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global data_store, scanner, ws_manager
    
    # 初始化
    data_store = DataStore()
    ws_manager = WebSocketManager()
    scanner = SessionScanner(data_store, ws_manager)
    
    # 启动扫描器
    scanner_task = asyncio.create_task(scanner.run())
    
    yield
    
    # 清理
    scanner.stop()
    scanner_task.cancel()
    try:
        await scanner_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="Agent Dashboard API",
    description="OpenClaw Agent团队监控系统",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== REST API ====================

@app.get("/api/stats")
async def get_stats():
    """获取系统统计信息"""
    return data_store.get_stats()

@app.get("/api/sessions")
async def get_sessions():
    """获取活跃会话列表"""
    return data_store.get_all_sessions()

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """获取会话详情"""
    session = data_store.get_session(session_id)
    if not session:
        return {"error": "Session not found"}
    return session

@app.get("/api/tasks")
async def get_tasks():
    """获取所有任务"""
    return data_store.get_all_tasks()

@app.get("/api/agents")
async def get_agents():
    """获取Agent注册表"""
    return data_store.get_agents()

@app.get("/api/history/{session_id}")
async def get_session_history(session_id: str, limit: int = 100):
    """获取会话历史数据"""
    return data_store.get_session_history(session_id, limit)

# ==================== WebSocket ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket实时推送"""
    await ws_manager.connect(websocket)
    try:
        # 发送初始数据
        await websocket.send_json({
            "type": "init",
            "data": {
                "sessions": data_store.get_all_sessions(),
                "stats": data_store.get_stats()
            }
        })
        
        # 保持连接并处理客户端消息
        while True:
            try:
                message = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )
                data = json.loads(message)
                
                # 处理客户端请求
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif data.get("type") == "subscribe":
                    # 订阅特定会话更新
                    session_id = data.get("session_id")
                    if session_id:
                        ws_manager.subscribe(websocket, session_id)
                        
            except asyncio.TimeoutError:
                # 发送心跳保持连接
                await websocket.send_json({"type": "heartbeat"})
                
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)

# ==================== 健康检查 ====================

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "sessions_count": len(data_store.get_all_sessions()),
        "scanner_running": scanner.is_running() if scanner else False
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
