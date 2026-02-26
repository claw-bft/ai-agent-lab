"""Main FastAPI application"""
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import (
    health_router,
    sessions_router,
    tasks_router,
    agents_router,
    websocket_router,
)
from app.routers.websocket import broadcast_update
from app.services import get_session_service, get_task_service, get_agent_service


# Background task for monitoring
monitoring_task = None


async def monitoring_loop():
    """Background task to monitor changes and broadcast updates"""
    last_session_count = 0
    last_task_count = 0
    
    while True:
        try:
            # Check for changes
            session_service = get_session_service()
            task_service = get_task_service()
            
            current_sessions = len(session_service.list_sessions())
            current_tasks = len(task_service.list_tasks())
            
            # Broadcast if changes detected
            if current_sessions != last_session_count:
                await broadcast_update("sessions_changed", {
                    "count": current_sessions,
                    "active": session_service.get_active_sessions_count()
                })
                last_session_count = current_sessions
            
            if current_tasks != last_task_count:
                await broadcast_update("tasks_changed", {
                    "count": current_tasks,
                    "stats": task_service.get_task_stats()
                })
                last_task_count = current_tasks
            
            # Wait before next check
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"Monitoring error: {e}")
            await asyncio.sleep(10)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print(f"Starting {app.title}...")
    
    # Start monitoring task
    global monitoring_task
    monitoring_task = asyncio.create_task(monitoring_loop())
    
    yield
    
    # Shutdown
    print(f"Shutting down {app.title}...")
    if monitoring_task:
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="Agent Team Visualization Dashboard API",
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health_router)
    app.include_router(sessions_router)
    app.include_router(tasks_router)
    app.include_router(agents_router)
    app.include_router(websocket_router)
    
    return app


# Create app instance
app = create_app()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Agent Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }
