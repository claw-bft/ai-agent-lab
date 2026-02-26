# Agent Dashboard Backend

FastAPI backend for Agent Team Visualization Dashboard.

## API Endpoints

### Health
- `GET /api/health` - Health check
- `GET /api/health/stats` - Dashboard statistics

### Sessions
- `GET /api/sessions` - List active sessions
- `GET /api/sessions/{id}` - Get session details

### Tasks
- `GET /api/tasks` - List all tasks
- `GET /api/tasks/{id}` - Get task details

### Agents
- `GET /api/agents` - List agents and their status
- `GET /api/agents/{id}` - Get agent details

### WebSocket
- `WS /ws` - Real-time updates

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python run.py

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Configuration
│   ├── models.py            # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── session_service.py   # Session data operations
│   │   ├── task_service.py      # Task data operations
│   │   └── agent_service.py     # Agent data operations
│   └── routers/
│       ├── __init__.py
│       ├── health.py        # Health check endpoints
│       ├── sessions.py      # Session endpoints
│       ├── tasks.py         # Task endpoints
│       ├── agents.py        # Agent endpoints
│       └── websocket.py     # WebSocket endpoint
├── requirements.txt
├── run.py                   # Standalone runner
├── .env.example             # Environment template
└── README.md
```

## Data Sources

The backend reads from:
- `/root/.openclaw/agents/main/sessions/*.jsonl` - Session transcripts
- `/root/.openclaw/shared/incoming/*.json` - Task definitions
- `/root/.openclaw/skills/` - Skill directories
- `/root/.openclaw/agents/` - Agent configurations

## WebSocket Protocol

Connect to `ws://localhost:8000/ws`

### Client → Server Messages
```json
{"type": "ping"}
{"type": "subscribe", "data": {"channels": ["sessions", "tasks"]}}
```

### Server → Client Messages
```json
{"type": "connected", "data": {"message": "..."}}
{"type": "pong", "data": {"timestamp": "..."}}
{"type": "sessions_changed", "data": {"count": 10, "active": 2}}
{"type": "tasks_changed", "data": {"count": 5, "stats": {...}}}
{"type": "heartbeat", "data": {"timestamp": "..."}}
```
