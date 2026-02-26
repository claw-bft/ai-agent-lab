import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Set
from pathlib import Path
import aiofiles

class SessionScanner:
    """会话扫描器 - 持续监控OpenClaw sessions目录"""
    
    def __init__(self, data_store, ws_manager):
        self.data_store = data_store
        self.ws_manager = ws_manager
        self.sessions_dir = Path(os.path.expanduser("~/.openclaw/sessions"))
        self.running = False
        self._known_sessions: Set[str] = set()
        self._scan_interval = 1.0  # 每秒扫描一次
        
    def is_running(self) -> bool:
        return self.running
    
    def stop(self):
        self.running = False
    
    async def run(self):
        """主循环 - 持续扫描"""
        self.running = True
        print(f"[Scanner] Started monitoring: {self.sessions_dir}")
        
        while self.running:
            try:
                await self._scan_sessions()
                await asyncio.sleep(self._scan_interval)
            except Exception as e:
                print(f"[Scanner] Error: {e}")
                await asyncio.sleep(5)  # 错误后等待更长时间
    
    async def _scan_sessions(self):
        """扫描会话目录"""
        if not self.sessions_dir.exists():
            return
        
        current_sessions = set()
        
        # 遍历所有会话目录
        for session_dir in self.sessions_dir.iterdir():
            if not session_dir.is_dir():
                continue
            
            session_id = session_dir.name
            current_sessions.add(session_id)
            
            # 读取会话信息
            session_data = await self._read_session_info(session_dir)
            
            # 检查是否为新会话或已更新
            existing = self.data_store.get_session(session_id)
            if not existing or self._has_changed(existing, session_data):
                self.data_store.update_session(session_id, session_data)
                
                # 通知WebSocket客户端
                await self.ws_manager.broadcast({
                    "type": "session_update",
                    "data": session_data
                })
                
                # 如果是新会话
                if session_id not in self._known_sessions:
                    self._known_sessions.add(session_id)
                    await self.ws_manager.broadcast({
                        "type": "session_new",
                        "data": session_data
                    })
                    print(f"[Scanner] New session detected: {session_id}")
        
        # 检测已关闭的会话
        closed_sessions = self._known_sessions - current_sessions
        for session_id in closed_sessions:
            self._known_sessions.discard(session_id)
            self.data_store.remove_session(session_id)
            
            await self.ws_manager.broadcast({
                "type": "session_closed",
                "data": {"id": session_id}
            })
            print(f"[Scanner] Session closed: {session_id}")
    
    async def _read_session_info(self, session_dir: Path) -> dict:
        """读取会话信息"""
        session_id = session_dir.name
        
        # 基础信息
        info = {
            "id": session_id,
            "name": session_id,
            "status": "active",
            "created_at": datetime.fromtimestamp(
                session_dir.stat().st_ctime
            ).isoformat(),
            "updated_at": datetime.now().isoformat(),
            "path": str(session_dir),
            "agent_type": "unknown",
            "metadata": {}
        }
        
        # 尝试读取session.json
        session_json = session_dir / "session.json"
        if session_json.exists():
            try:
                async with aiofiles.open(session_json, 'r') as f:
                    content = await f.read()
                    data = json.loads(content)
                    info.update({
                        "name": data.get("label", session_id),
                        "agent_type": data.get("agent", "unknown"),
                        "metadata": data
                    })
            except Exception as e:
                print(f"[Scanner] Error reading {session_json}: {e}")
        
        # 检查是否有任务文件
        tasks_file = session_dir / "tasks.json"
        if tasks_file.exists():
            try:
                async with aiofiles.open(tasks_file, 'r') as f:
                    content = await f.read()
                    tasks = json.loads(content)
                    info["tasks_count"] = len(tasks)
                    info["tasks"] = tasks
            except:
                pass
        
        # 检查内存文件
        memory_dir = session_dir / "memory"
        if memory_dir.exists():
            info["has_memory"] = True
            info["memory_files"] = len(list(memory_dir.glob("*.md")))
        
        return info
    
    def _has_changed(self, old: dict, new: dict) -> bool:
        """检查会话数据是否有变化"""
        # 比较关键字段
        key_fields = ["status", "agent_type", "tasks_count", "memory_files"]
        for field in key_fields:
            if old.get(field) != new.get(field):
                return True
        return False
