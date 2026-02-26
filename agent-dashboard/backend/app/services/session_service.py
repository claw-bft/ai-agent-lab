"""Session service for managing session data from JSONL files"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from app.models import SessionInfo, SessionDetail, MessageType
from app.config import get_settings


class SessionService:
    """Service for session data operations"""
    
    def __init__(self):
        self.settings = get_settings()
        self.sessions_dir = Path(self.settings.SESSIONS_DIR)
    
    def list_sessions(self) -> List[SessionInfo]:
        """List all sessions from JSONL files"""
        sessions = []
        
        if not self.sessions_dir.exists():
            return sessions
        
        for file_path in self.sessions_dir.glob("*.jsonl"):
            # Skip lock files and deleted sessions
            if file_path.name.endswith(".lock") or ".deleted." in file_path.name:
                continue
                
            session_info = self._parse_session_file(file_path)
            if session_info:
                sessions.append(session_info)
        
        # Sort by updated_at desc
        sessions.sort(key=lambda x: x.updated_at or datetime.min, reverse=True)
        return sessions
    
    def get_session(self, session_id: str) -> Optional[SessionDetail]:
        """Get detailed session information"""
        file_path = self.sessions_dir / f"{session_id}.jsonl"
        
        if not file_path.exists():
            # Try to find with deleted suffix
            for fp in self.sessions_dir.glob(f"{session_id}*.jsonl"):
                if not fp.name.endswith(".lock"):
                    file_path = fp
                    break
        
        if not file_path.exists():
            return None
        
        return self._parse_session_detail(file_path)
    
    def _parse_session_file(self, file_path: Path) -> Optional[SessionInfo]:
        """Parse a session JSONL file for basic info"""
        try:
            stat = file_path.stat()
            file_size = stat.st_size
            
            # Check for lock file
            lock_file = Path(str(file_path) + ".lock")
            is_locked = lock_file.exists()
            
            # Parse first and last few lines for metadata
            messages = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            msg = json.loads(line)
                            messages.append(msg)
                        except json.JSONDecodeError:
                            continue
            
            if not messages:
                return None
            
            # Extract session info
            session_id = self._extract_session_id(file_path.name)
            session_key = None
            created_at = None
            updated_at = None
            model = None
            provider = None
            
            # First message usually contains session info
            first_msg = messages[0]
            if first_msg.get("type") == "session":
                session_key = first_msg.get("id")
                created_at = self._parse_timestamp(first_msg.get("timestamp"))
            
            # Last message for updated_at
            last_msg = messages[-1]
            updated_at = self._parse_timestamp(last_msg.get("timestamp"))
            
            # Extract model info
            for msg in messages:
                if msg.get("type") == "model_change":
                    model = msg.get("data", {}).get("modelId") or msg.get("modelId")
                    provider = msg.get("data", {}).get("provider") or msg.get("provider")
                    break
            
            # Determine status
            status = "active" if is_locked else "completed"
            if any(m.get("type") == "error" for m in messages):
                status = "error"
            
            return SessionInfo(
                id=session_id,
                session_key=session_key,
                status=status,
                created_at=created_at,
                updated_at=updated_at,
                message_count=len(messages),
                file_size=file_size,
                file_path=str(file_path),
                is_locked=is_locked
            )
            
        except Exception as e:
            print(f"Error parsing session file {file_path}: {e}")
            return None
    
    def _parse_session_detail(self, file_path: Path) -> Optional[SessionDetail]:
        """Parse full session details"""
        basic_info = self._parse_session_file(file_path)
        if not basic_info:
            return None
        
        messages = []
        metadata = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            msg = json.loads(line)
                            messages.append(msg)
                            
                            # Extract metadata from session message
                            if msg.get("type") == "session":
                                metadata = msg.get("data", {})
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"Error reading session file {file_path}: {e}")
        
        # Extract model info
        model = None
        provider = None
        for msg in messages:
            if msg.get("type") == "model_change":
                model = msg.get("data", {}).get("modelId") or msg.get("modelId")
                provider = msg.get("data", {}).get("provider") or msg.get("provider")
                break
        
        return SessionDetail(
            id=basic_info.id,
            session_key=basic_info.session_key,
            status=basic_info.status,
            created_at=basic_info.created_at,
            updated_at=basic_info.updated_at,
            message_count=len(messages),
            file_size=basic_info.file_size,
            file_path=str(file_path),
            is_locked=basic_info.is_locked,
            messages=messages,
            metadata=metadata,
            model=model,
            provider=provider
        )
    
    def _extract_session_id(self, filename: str) -> str:
        """Extract session ID from filename"""
        # Remove .jsonl extension and any .deleted suffix
        name = filename.replace(".jsonl", "")
        if ".deleted." in name:
            name = name.split(".deleted.")[0]
        return name
    
    def _parse_timestamp(self, ts: Any) -> Optional[datetime]:
        """Parse timestamp from various formats"""
        if not ts:
            return None
        
        try:
            if isinstance(ts, (int, float)):
                # Unix timestamp in milliseconds
                return datetime.fromtimestamp(ts / 1000)
            elif isinstance(ts, str):
                # ISO format
                return datetime.fromisoformat(ts.replace('Z', '+00:00'))
        except Exception:
            pass
        
        return None
    
    def get_active_sessions_count(self) -> int:
        """Get count of active (locked) sessions"""
        count = 0
        if self.sessions_dir.exists():
            for file_path in self.sessions_dir.glob("*.jsonl.lock"):
                count += 1
        return count


# Singleton instance
_session_service = None


def get_session_service() -> SessionService:
    """Get session service singleton"""
    global _session_service
    if _session_service is None:
        _session_service = SessionService()
    return _session_service
