import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

class DataStore:
    """数据存储管理 - SQLite + 内存缓存"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.expanduser("~/.openclaw/agent_dashboard.db")
        self._init_db()
        
        # 内存缓存
        self._sessions: Dict[str, dict] = {}
        self._tasks: Dict[str, dict] = {}
        self._agents: Dict[str, dict] = {}
        
    def _init_db(self):
        """初始化数据库"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 会话表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                name TEXT,
                agent_type TEXT,
                status TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                metadata TEXT,
                data TEXT
            )
        ''')
        
        # 历史数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TIMESTAMP,
                event_type TEXT,
                data TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        ''')
        
        # Agent注册表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT,
                type TEXT,
                description TEXT,
                created_at TIMESTAMP,
                last_seen TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # 任务表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                name TEXT,
                status TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def update_session(self, session_id: str, data: dict):
        """更新会话数据"""
        self._sessions[session_id] = {
            **data,
            "updated_at": datetime.now().isoformat()
        }
        
        # 持久化到数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO sessions 
            (id, name, agent_type, status, created_at, updated_at, metadata, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            data.get('name', ''),
            data.get('agent_type', ''),
            data.get('status', 'unknown'),
            data.get('created_at', datetime.now().isoformat()),
            datetime.now().isoformat(),
            json.dumps(data.get('metadata', {})),
            json.dumps(data)
        ))
        conn.commit()
        conn.close()
    
    def remove_session(self, session_id: str):
        """移除会话"""
        if session_id in self._sessions:
            del self._sessions[session_id]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        conn.commit()
        conn.close()
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """获取单个会话"""
        return self._sessions.get(session_id)
    
    def get_all_sessions(self) -> List[dict]:
        """获取所有会话"""
        return list(self._sessions.values())
    
    def add_history(self, session_id: str, event_type: str, data: dict):
        """添加历史记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO session_history (session_id, timestamp, event_type, data)
            VALUES (?, ?, ?, ?)
        ''', (session_id, datetime.now().isoformat(), event_type, json.dumps(data)))
        conn.commit()
        conn.close()
    
    def get_session_history(self, session_id: str, limit: int = 100) -> List[dict]:
        """获取会话历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, event_type, data 
            FROM session_history 
            WHERE session_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (session_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "timestamp": row[0],
                "event_type": row[1],
                "data": json.loads(row[2])
            }
            for row in rows
        ]
    
    def update_task(self, task_id: str, data: dict):
        """更新任务"""
        self._tasks[task_id] = {
            **data,
            "updated_at": datetime.now().isoformat()
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO tasks 
            (id, session_id, name, status, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_id,
            data.get('session_id', ''),
            data.get('name', ''),
            data.get('status', 'pending'),
            data.get('created_at', datetime.now().isoformat()),
            datetime.now().isoformat(),
            json.dumps(data)
        ))
        conn.commit()
        conn.close()
    
    def get_all_tasks(self) -> List[dict]:
        """获取所有任务"""
        return list(self._tasks.values())
    
    def register_agent(self, agent_id: str, data: dict):
        """注册Agent"""
        self._agents[agent_id] = {
            **data,
            "last_seen": datetime.now().isoformat()
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO agents 
            (id, name, type, description, created_at, last_seen, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            agent_id,
            data.get('name', ''),
            data.get('type', ''),
            data.get('description', ''),
            data.get('created_at', datetime.now().isoformat()),
            datetime.now().isoformat(),
            json.dumps(data)
        ))
        conn.commit()
        conn.close()
    
    def get_agents(self) -> List[dict]:
        """获取所有Agent"""
        return list(self._agents.values())
    
    def get_stats(self) -> dict:
        """获取系统统计"""
        sessions = self.get_all_sessions()
        tasks = self.get_all_tasks()
        agents = self.get_agents()
        
        # 状态统计
        status_counts = {}
        for s in sessions:
            status = s.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_sessions": len(sessions),
            "total_tasks": len(tasks),
            "total_agents": len(agents),
            "status_distribution": status_counts,
            "timestamp": datetime.now().isoformat()
        }
