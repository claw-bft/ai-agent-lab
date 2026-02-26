from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import json
import os
import glob
import subprocess
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import psutil

# Data models
class Agent(BaseModel):
    id: str
    name: str
    status: str
    currentTask: Optional[str] = None
    completedTasks: int = 0
    failedTasks: int = 0
    totalTokens: int = 0
    avgResponseTime: float = 0.0
    lastActive: str

class Task(BaseModel):
    id: str
    agentId: str
    agentName: str
    status: str
    type: str
    input: str
    output: Optional[str] = None
    startTime: str
    endTime: Optional[str] = None
    duration: Optional[int] = None
    tokensUsed: int = 0
    error: Optional[str] = None

class Session(BaseModel):
    id: str
    agentId: str
    agentName: str
    status: str
    startTime: str
    lastActivity: str
    taskCount: int

class SystemHealth(BaseModel):
    status: str
    activeSessions: int
    totalAgents: int
    runningTasks: int
    queuedTasks: int
    cpuUsage: float
    memoryUsage: float
    uptime: int

class CronJob(BaseModel):
    id: str
    name: str
    schedule: str
    command: str
    enabled: bool
    lastRun: Optional[str] = None
    nextRun: Optional[str] = None
    lastStatus: Optional[str] = None

# Connection manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# Helper functions to read OpenClaw data
def get_sessions_list():
    """Get active sessions from OpenClaw"""
    try:
        result = subprocess.run(
            ['openclaw', 'sessions', 'list', '--json'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return []
    except Exception as e:
        print(f"Error getting sessions: {e}")
        return []

def get_cron_list():
    """Get cron jobs from OpenClaw"""
    try:
        result = subprocess.run(
            ['openclaw', 'cron', 'list', '--json'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return []
    except Exception as e:
        print(f"Error getting cron jobs: {e}")
        return []

def get_session_history():
    """Get session history from OpenClaw"""
    try:
        result = subprocess.run(
            ['openclaw', 'sessions', 'history', '--json'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return []
    except Exception as e:
        print(f"Error getting session history: {e}")
        return []

def read_session_transcript(session_id: str):
    """Read session transcript from file system"""
    try:
        # Look for session files in workspace
        workspace = os.path.expanduser('~/.openclaw/workspace')
        pattern = f"{workspace}/.sessions/{session_id}*"
        files = glob.glob(pattern)
        
        if files:
            # Read the most recent file
            files.sort(key=os.path.getmtime, reverse=True)
            with open(files[0], 'r') as f:
                return f.read()
        return None
    except Exception as e:
        print(f"Error reading transcript: {e}")
        return None

def parse_agents_from_sessions(sessions: list) -> List[Agent]:
    """Parse agent information from sessions"""
    agents_dict = {}
    
    for session in sessions:
        agent_id = session.get('agent', 'unknown')
        if agent_id not in agents_dict:
            agents_dict[agent_id] = {
                'id': agent_id,
                'name': agent_id,
                'status': 'idle',
                'completedTasks': 0,
                'failedTasks': 0,
                'totalTokens': 0,
                'avgResponseTime': 0,
                'lastActive': session.get('created', datetime.now().isoformat()),
                'tasks': []
            }
        
        # Update status based on session state
        state = session.get('state', 'unknown')
        if state == 'running':
            agents_dict[agent_id]['status'] = 'active'
            agents_dict[agent_id]['currentTask'] = session.get('description', 'Unknown task')
        
        agents_dict[agent_id]['lastActive'] = session.get('updated', agents_dict[agent_id]['lastActive'])
    
    return [Agent(**agent) for agent in agents_dict.values()]

def parse_tasks_from_sessions(sessions: list) -> List[Task]:
    """Parse task information from sessions"""
    tasks = []
    
    for session in sessions:
        task = Task(
            id=session.get('id', 'unknown'),
            agentId=session.get('agent', 'unknown'),
            agentName=session.get('agent', 'unknown'),
            status='running' if session.get('state') == 'running' else 'completed',
            type=session.get('type', 'unknown'),
            input=session.get('description', 'No description'),
            startTime=session.get('created', datetime.now().isoformat()),
            endTime=session.get('ended') if session.get('state') != 'running' else None,
            duration=session.get('duration_ms'),
            tokensUsed=session.get('tokens', 0)
        )
        tasks.append(task)
    
    return tasks

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    asyncio.create_task(broadcast_updates())
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Agent Dashboard API",
    description="API for Agent Team Dashboard",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def broadcast_updates():
    """Broadcast updates to all connected WebSocket clients"""
    while True:
        try:
            # Get current data
            sessions = get_sessions_list()
            tasks = parse_tasks_from_sessions(sessions)
            
            await manager.broadcast({
                "type": "update",
                "payload": {
                    "timestamp": datetime.now().isoformat(),
                    "activeSessions": len(sessions),
                    "runningTasks": len([t for t in tasks if t.status == 'running'])
                }
            })
        except Exception as e:
            print(f"Broadcast error: {e}")
        
        await asyncio.sleep(5)  # Update every 5 seconds

# Health check endpoint
@app.get("/api/health", response_model=SystemHealth)
async def get_health():
    """Get system health status"""
    sessions = get_sessions_list()
    tasks = parse_tasks_from_sessions(sessions)
    agents = parse_agents_from_sessions(sessions)
    
    # Get system stats
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    # Determine health status
    status = 'healthy'
    if cpu_percent > 80 or memory.percent > 85:
        status = 'warning'
    if cpu_percent > 95 or memory.percent > 95:
        status = 'critical'
    
    # Get uptime (simplified - in production would track actual start time)
    boot_time = psutil.boot_time()
    uptime = int(datetime.now().timestamp() - boot_time)
    
    return SystemHealth(
        status=status,
        activeSessions=len(sessions),
        totalAgents=len(agents),
        runningTasks=len([t for t in tasks if t.status == 'running']),
        queuedTasks=len([t for t in tasks if t.status == 'pending']),
        cpuUsage=cpu_percent,
        memoryUsage=memory.percent,
        uptime=uptime
    )

# Agent endpoints
@app.get("/api/agents", response_model=List[Agent])
async def get_agents():
    """Get all agents"""
    sessions = get_sessions_list()
    return parse_agents_from_sessions(sessions)

@app.get("/api/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """Get agent by ID"""
    sessions = get_sessions_list()
    agents = parse_agents_from_sessions(sessions)
    for agent in agents:
        if agent.id == agent_id:
            return agent
    return JSONResponse(status_code=404, content={"error": "Agent not found"})

@app.get("/api/agents/stats")
async def get_agent_stats():
    """Get agent statistics"""
    sessions = get_sessions_list()
    agents = parse_agents_from_sessions(sessions)
    
    total_completed = sum(a.completedTasks for a in agents)
    total_failed = sum(a.failedTasks for a in agents)
    
    return {
        "agents": [a.dict() for a in agents],
        "totalCompleted": total_completed,
        "totalFailed": total_failed
    }

# Task endpoints
@app.get("/api/tasks", response_model=List[Task])
async def get_tasks(status: Optional[str] = None, agent_id: Optional[str] = None, search: Optional[str] = None):
    """Get all tasks with optional filtering"""
    sessions = get_sessions_list()
    history = get_session_history()
    all_sessions = sessions + history
    
    tasks = parse_tasks_from_sessions(all_sessions)
    
    # Apply filters
    if status and status != 'all':
        tasks = [t for t in tasks if t.status == status]
    if agent_id:
        tasks = [t for t in tasks if t.agentId == agent_id]
    if search:
        search_lower = search.lower()
        tasks = [t for t in tasks if search_lower in t.input.lower()]
    
    return tasks

@app.get("/api/tasks/running", response_model=List[Task])
async def get_running_tasks():
    """Get running tasks"""
    sessions = get_sessions_list()
    tasks = parse_tasks_from_sessions(sessions)
    return [t for t in tasks if t.status == 'running']

@app.get("/api/tasks/recent")
async def get_recent_tasks(limit: int = 10):
    """Get recent completed tasks"""
    history = get_session_history()
    tasks = parse_tasks_from_sessions(history)
    tasks.sort(key=lambda x: x.endTime or '', reverse=True)
    return tasks[:limit]

@app.get("/api/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """Get task by ID"""
    sessions = get_sessions_list()
    history = get_session_history()
    all_sessions = sessions + history
    
    tasks = parse_tasks_from_sessions(all_sessions)
    for task in tasks:
        if task.id == task_id:
            return task
    return JSONResponse(status_code=404, content={"error": "Task not found"})

# Session endpoints
@app.get("/api/sessions", response_model=List[Session])
async def get_sessions():
    """Get all sessions"""
    sessions = get_sessions_list()
    return [
        Session(
            id=s.get('id', ''),
            agentId=s.get('agent', ''),
            agentName=s.get('agent', ''),
            status='active' if s.get('state') == 'running' else 'completed',
            startTime=s.get('created', ''),
            lastActivity=s.get('updated', ''),
            taskCount=1
        )
        for s in sessions
    ]

@app.get("/api/sessions/active", response_model=List[Session])
async def get_active_sessions():
    """Get active sessions"""
    sessions = get_sessions_list()
    return [
        Session(
            id=s.get('id', ''),
            agentId=s.get('agent', ''),
            agentName=s.get('agent', ''),
            status='active',
            startTime=s.get('created', ''),
            lastActivity=s.get('updated', ''),
            taskCount=1
        )
        for s in sessions if s.get('state') == 'running'
    ]

@app.get("/api/sessions/history", response_model=List[Session])
async def get_sessions_history():
    """Get session history"""
    history = get_session_history()
    return [
        Session(
            id=s.get('id', ''),
            agentId=s.get('agent', ''),
            agentName=s.get('agent', ''),
            status='completed',
            startTime=s.get('created', ''),
            lastActivity=s.get('ended', s.get('updated', '')),
            taskCount=1
        )
        for s in history
    ]

# Cron endpoints
@app.get("/api/cron", response_model=List[CronJob])
async def get_cron_jobs():
    """Get all cron jobs"""
    cron_list = get_cron_list()
    return [
        CronJob(
            id=c.get('id', str(i)),
            name=c.get('name', f'Job {i}'),
            schedule=c.get('schedule', ''),
            command=c.get('command', ''),
            enabled=c.get('enabled', True),
            lastRun=c.get('last_run'),
            nextRun=c.get('next_run'),
            lastStatus=c.get('last_status')
        )
        for i, c in enumerate(cron_list)
    ]

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle any client messages
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # Handle any specific client requests
                if message.get('action') == 'ping':
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)