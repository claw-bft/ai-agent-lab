"""Task service for managing task data from JSON files"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any
from app.models import TaskInfo, TaskStatus
from app.config import get_settings


class TaskService:
    """Service for task data operations"""
    
    def __init__(self):
        self.settings = get_settings()
        self.tasks_dir = Path(self.settings.TASKS_DIR)
    
    def list_tasks(self) -> List[TaskInfo]:
        """List all tasks from JSON files"""
        tasks = []
        
        if not self.tasks_dir.exists():
            return tasks
        
        for file_path in self.tasks_dir.glob("*.json"):
            task_info = self._parse_task_file(file_path)
            if task_info:
                tasks.append(task_info)
        
        # Sort by updated_at desc
        tasks.sort(key=lambda x: x.updated_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        return tasks
    
    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """Get task by ID"""
        # Try exact match first
        file_path = self.tasks_dir / f"{task_id}.json"
        
        if not file_path.exists():
            # Search in all JSON files
            for fp in self.tasks_dir.glob("*.json"):
                try:
                    with open(fp, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get("task_id") == task_id:
                            return self._parse_task_data(data, fp)
                except Exception:
                    continue
            return None
        
        return self._parse_task_file(file_path)
    
    def _parse_task_file(self, file_path: Path) -> Optional[TaskInfo]:
        """Parse a task JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self._parse_task_data(data, file_path)
        except Exception as e:
            print(f"Error parsing task file {file_path}: {e}")
            return None
    
    def _parse_task_data(self, data: Dict[str, Any], file_path: Path) -> Optional[TaskInfo]:
        """Parse task data from dict"""
        try:
            task_id = data.get("task_id") or data.get("id") or file_path.stem
            
            # Parse timestamps
            created_at = self._parse_timestamp(data.get("timestamp") or data.get("created_at"))
            updated_at = self._parse_timestamp(data.get("updated_at"))
            deadline = self._parse_timestamp(data.get("deadline"))
            
            # Determine status based on data
            status = TaskStatus.PENDING
            if data.get("completed"):
                status = TaskStatus.COMPLETED
            elif data.get("error") or data.get("failed"):
                status = TaskStatus.FAILED
            elif data.get("running"):
                status = TaskStatus.RUNNING
            
            # Check if deadline passed
            if deadline and deadline < datetime.now(timezone.utc) and status == TaskStatus.PENDING:
                status = TaskStatus.TIMEOUT
            
            return TaskInfo(
                id=task_id,
                name=data.get("task_name") or data.get("name"),
                task_type=data.get("task_type"),
                status=status,
                created_at=created_at,
                updated_at=updated_at or created_at,
                requester=data.get("requester"),
                workflow=data.get("workflow"),
                steps=data.get("steps", []),
                file_path=str(file_path)
            )
            
        except Exception as e:
            print(f"Error parsing task data: {e}")
            return None
    
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
    
    def get_task_stats(self) -> Dict[str, int]:
        """Get task statistics"""
        tasks = self.list_tasks()
        return {
            "total": len(tasks),
            "pending": sum(1 for t in tasks if t.status == TaskStatus.PENDING),
            "running": sum(1 for t in tasks if t.status == TaskStatus.RUNNING),
            "completed": sum(1 for t in tasks if t.status == TaskStatus.COMPLETED),
            "failed": sum(1 for t in tasks if t.status == TaskStatus.FAILED),
        }


# Singleton instance
_task_service = None


def get_task_service() -> TaskService:
    """Get task service singleton"""
    global _task_service
    if _task_service is None:
        _task_service = TaskService()
    return _task_service
