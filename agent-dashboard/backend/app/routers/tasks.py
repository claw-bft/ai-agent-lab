"""Tasks router"""
from typing import List
from fastapi import APIRouter, HTTPException
from app.models import TaskInfo
from app.services import get_task_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=List[TaskInfo])
async def list_tasks():
    """List all tasks"""
    service = get_task_service()
    return service.list_tasks()


@router.get("/{task_id}", response_model=TaskInfo)
async def get_task(task_id: str):
    """Get task by ID"""
    service = get_task_service()
    task = service.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return task
