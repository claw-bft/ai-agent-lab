"""Health check router"""
import time
from datetime import datetime
from fastapi import APIRouter
from app.models import HealthStatus, StatsSummary
from app.services import get_session_service, get_task_service, get_agent_service

router = APIRouter(prefix="/api/health", tags=["health"])

# Server start time for uptime calculation
START_TIME = datetime.now()


@router.get("", response_model=HealthStatus)
async def health_check():
    """Health check endpoint"""
    uptime = (datetime.now() - START_TIME).total_seconds()
    
    return HealthStatus(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now(),
        uptime_seconds=uptime
    )


@router.get("/stats", response_model=StatsSummary)
async def get_stats():
    """Get dashboard statistics summary"""
    session_service = get_session_service()
    task_service = get_task_service()
    agent_service = get_agent_service()
    
    sessions = session_service.list_sessions()
    task_stats = task_service.get_task_stats()
    agent_stats = agent_service.get_agent_stats()
    
    return StatsSummary(
        total_sessions=len(sessions),
        active_sessions=session_service.get_active_sessions_count(),
        total_tasks=task_stats["total"],
        pending_tasks=task_stats["pending"],
        running_tasks=task_stats["running"],
        total_agents=agent_stats["total"],
        busy_agents=agent_stats["busy"]
    )
