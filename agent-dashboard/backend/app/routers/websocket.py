"""WebSocket router for real-time updates"""
import asyncio
import json
from datetime import datetime
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["websocket"])

# Store active WebSocket connections
active_connections: Set[WebSocket] = set()


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections.discard(conn)
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        # Send initial connection success message
        await manager.send_personal_message({
            "type": "connected",
            "data": {
                "message": "Connected to Agent Dashboard",
                "timestamp": datetime.now().isoformat()
            }
        }, websocket)
        
        # Handle incoming messages
        while True:
            try:
                # Receive message with timeout
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )
                
                # Parse and handle message
                try:
                    message = json.loads(data)
                    await handle_client_message(message, websocket)
                except json.JSONDecodeError:
                    await manager.send_personal_message({
                        "type": "error",
                        "data": {"message": "Invalid JSON format"}
                    }, websocket)
                    
            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                await manager.send_personal_message({
                    "type": "heartbeat",
                    "data": {"timestamp": datetime.now().isoformat()}
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def handle_client_message(message: dict, websocket: WebSocket):
    """Handle messages from client"""
    msg_type = message.get("type", "unknown")
    
    if msg_type == "ping":
        await manager.send_personal_message({
            "type": "pong",
            "data": {"timestamp": datetime.now().isoformat()}
        }, websocket)
    
    elif msg_type == "subscribe":
        # Handle subscription to specific events
        channels = message.get("data", {}).get("channels", [])
        await manager.send_personal_message({
            "type": "subscribed",
            "data": {"channels": channels}
        }, websocket)
    
    else:
        await manager.send_personal_message({
            "type": "ack",
            "data": {"received": msg_type}
        }, websocket)


async def broadcast_update(update_type: str, data: dict):
    """Broadcast an update to all connected clients"""
    await manager.broadcast({
        "type": update_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    })
