#!/usr/bin/env python3
"""
Agent Dashboard Monitor
后台常驻监控进程 - 每秒扫描OpenClaw sessions目录
"""

import os
import sys
import json
import time
import signal
import sqlite3
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, Optional
import aiofiles

# 配置
SESSIONS_DIR = Path(os.path.expanduser("~/.openclaw/sessions"))
DB_PATH = os.path.expanduser("~/.openclaw/agent_dashboard.db")
BACKEND_URL = "http://localhost:8000"
SCAN_INTERVAL = 1.0  # 每秒扫描

class Monitor:
    """监控进程主类"""
    
    def __init__(self):
        self.running = False
        self._known_sessions: Set[str] = set()
        self._session_states: Dict[str, dict] = {}
        self._init_db()
        
    def _init_db(self):
        """初始化SQLite数据库"""
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 历史数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT,
                status TEXT,
                data TEXT
            )
        ''')
        
        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_session_history_session_id 
            ON session_history(session_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_session_history_timestamp 
            ON session_history(timestamp)
        ''')
        
        conn.commit()
        conn.close()
        print(f"[Monitor] Database initialized: {DB_PATH}")
    
    def _log_history(self, session_id: str, event_type: str, status: str, data: dict):
        """记录历史数据"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO session_history (session_id, event_type, status, data)
            VALUES (?, ?, ?, ?)
        ''', (session_id, event_type, status, json.dumps(data)))
        conn.commit()
        conn.close()
    
    async def run(self):
        """主循环"""
        self.running = True
        print(f"[Monitor] Started monitoring: {SESSIONS_DIR}")
        print(f"[Monitor] Scan interval: {SCAN_INTERVAL}s")
        
        # 确保目录存在
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        
        while self.running:
            try:
                await self._scan_once()
                await asyncio.sleep(SCAN_INTERVAL)
            except Exception as e:
                print(f"[Monitor] Error: {e}")
                await asyncio.sleep(5)
    
    async def _scan_once(self):
        """执行一次扫描"""
        if not SESSIONS_DIR.exists():
            return
        
        current_sessions = set()
        
        for session_dir in SESSIONS_DIR.iterdir():
            if not session_dir.is_dir():
                continue
            
            session_id = session_dir.name
            current_sessions.add(session_id)
            
            # 读取会话信息
            session_data = await self._read_session(session_dir)
            
            # 检测变化
            if session_id not in self._known_sessions:
                # 新会话
                print(f"[Monitor] New session: {session_id} ({session_data.get('name', 'unknown')})")
                self._log_history(session_id, "created", session_data.get('status', 'unknown'), session_data)
                await self._notify_backend("session_new", session_data)
                self._known_sessions.add(session_id)
                
            elif self._has_changed(self._session_states.get(session_id, {}), session_data):
                # 状态变化
                print(f"[Monitor] Session updated: {session_id}")
                self._log_history(session_id, "updated", session_data.get('status', 'unknown'), session_data)
                await self._notify_backend("session_update", session_data)
            
            self._session_states[session_id] = session_data
        
        # 检测关闭的会话
        closed = self._known_sessions - current_sessions
        for session_id in closed:
            print(f"[Monitor] Session closed: {session_id}")
            self._log_history(session_id, "closed", "closed", {"id": session_id})
            await self._notify_backend("session_closed", {"id": session_id})
            self._known_sessions.discard(session_id)
            if session_id in self._session_states:
                del self._session_states[session_id]
    
    async def _read_session(self, session_dir: Path) -> dict:
        """读取会话信息"""
        session_id = session_dir.name
        
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
        
        # 读取session.json
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
                pass
        
        # 检查任务
        tasks_file = session_dir / "tasks.json"
        if tasks_file.exists():
            try:
                async with aiofiles.open(tasks_file, 'r') as f:
                    content = await f.read()
                    tasks = json.loads(content)
                    info["tasks_count"] = len(tasks)
            except:
                pass
        
        # 检查内存文件
        memory_dir = session_dir / "memory"
        if memory_dir.exists():
            info["memory_files"] = len(list(memory_dir.glob("*.md")))
        
        # 检查最近活动
        activity_file = session_dir / ".last_activity"
        if activity_file.exists():
            try:
                mtime = activity_file.stat().st_mtime
                info["last_activity"] = datetime.fromtimestamp(mtime).isoformat()
                # 如果超过5分钟无活动，标记为idle
                if time.time() - mtime > 300:
                    info["status"] = "idle"
            except:
                pass
        
        return info
    
    def _has_changed(self, old: dict, new: dict) -> bool:
        """检查是否有变化"""
        fields = ["status", "agent_type", "tasks_count", "memory_files", "name"]
        for f in fields:
            if old.get(f) != new.get(f):
                return True
        return False
    
    async def _notify_backend(self, event_type: str, data: dict):
        """通知Backend服务"""
        try:
            async with aiohttp.ClientSession() as session:
                # 这里可以调用Backend的API
                # 目前Backend的scanner已经处理了大部分逻辑
                # Monitor主要负责历史记录
                pass
        except Exception as e:
            print(f"[Monitor] Backend notify error: {e}")
    
    def stop(self):
        """停止监控"""
        self.running = False
        print("[Monitor] Stopping...")

def signal_handler(monitor: Monitor):
    """信号处理"""
    def handler(signum, frame):
        print(f"\n[Monitor] Received signal {signum}")
        monitor.stop()
        sys.exit(0)
    return handler

async def main():
    monitor = Monitor()
    
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler(monitor))
    signal.signal(signal.SIGTERM, signal_handler(monitor))
    
    await monitor.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Monitor] Interrupted by user")
        sys.exit(0)
