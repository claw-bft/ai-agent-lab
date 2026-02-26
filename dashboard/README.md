# OpenClaw WebSocket Dashboard

Real-time interactive dashboard with WebSocket bidirectional communication.

## Architecture

```
Browser ←→ WebSocket ←→ Backend (Python) ←→ OpenClaw
```

## Features

- **Real-time Updates**: Live system stats, tasks, skills, and file updates
- **Interactive Tasks**: Create, update, delete tasks with real-time sync
- **File Explorer**: Browse and edit workspace files
- **Terminal**: Execute safe shell commands
- **Chat**: Real-time messaging between connected clients
- **Auto-reconnect**: Automatic reconnection on connection loss

## Quick Start

### 1. Install Dependencies

```bash
cd /root/.openclaw/workspace/dashboard
./deploy.sh install
```

Or manually:
```bash
pip3 install websockets psutil
```

### 2. Start Server

```bash
./deploy.sh start
```

Or manually:
```bash
python3 backend_ws.py
```

### 3. Open Frontend

Open `frontend_ws.html` in your browser:
```bash
# Linux
xdg-open frontend_ws.html

# macOS
open frontend_ws.html

# Windows
start frontend_ws.html
```

Or serve via Python:
```bash
python3 -m http.server 8080
# Then open http://localhost:8080/frontend_ws.html
```

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `WS_HOST` | `0.0.0.0` | WebSocket server host |
| `WS_PORT` | `8000` | WebSocket server port |
| `WORKSPACE_DIR` | `/root/.openclaw/workspace` | Workspace directory |

## API Protocol

### Client → Server Messages

```json
{"type": "ping"}
{"type": "get_stats"}
{"type": "get_tasks"}
{"type": "create_task", "data": {"title": "New Task"}}
{"type": "update_task", "id": "task-id", "data": {"status": "done"}}
{"type": "delete_task", "id": "task-id"}
{"type": "get_skills"}
{"type": "get_files"}
{"type": "read_file", "path": "README.md"}
{"type": "write_file", "path": "test.txt", "content": "Hello"}
{"type": "execute_command", "command": "ls -la"}
{"type": "chat_message", "role": "user", "content": "Hello"}
```

### Server → Client Messages

```json
{"type": "connected", "data": {"client_id": "abc123"}}
{"type": "stats_update", "data": {"cpu_percent": 45, "memory": {...}}}
{"type": "tasks", "data": [...]}
{"type": "task_created", "data": {...}}
{"type": "task_updated", "data": {...}}
{"type": "task_deleted", "data": {"id": "task-id"}}
{"type": "skills", "data": [...]}
{"type": "files", "data": [...]}
{"type": "file_content", "data": {"path": "...", "content": "..."}}
{"type": "chat_message", "data": {...}}
{"type": "clients_update", "data": {"count": 5}}
{"type": "error", "data": {"message": "..."}}
```

## Deployment Options

### Option 1: Direct Python
```bash
python3 backend_ws.py
```

### Option 2: Using Deploy Script
```bash
./deploy.sh start
```

### Option 3: Systemd Service
```bash
./deploy.sh install
sudo systemctl start openclaw-dashboard
sudo systemctl enable openclaw-dashboard
```

### Option 4: Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend_ws.py .
RUN pip install websockets psutil
EXPOSE 8000
CMD ["python", "backend_ws.py"]
```

## Port Configuration

If port 8000 is blocked by firewall:

1. **Use port 80 or 443** (usually open):
```bash
sudo WS_PORT=80 python3 backend_ws.py
```

2. **Configure firewall**:
```bash
# Ubuntu/Debian
sudo ufw allow 8000/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# iptables
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
```

3. **Cloud provider security group**: Add inbound rule for port 8000

## Troubleshooting

### Connection Refused
- Check if server is running: `./deploy.sh status`
- Check firewall settings
- Verify port is not in use: `lsof -i :8000`

### WebSocket Errors
- Check browser console for errors
- Verify WebSocket URL matches server host/port
- Check server logs: `tail -f dashboard.log`

### Permission Denied
- Ensure workspace directory is readable/writable
- Check file permissions for TASKS.md

## Files

- `backend_ws.py` - WebSocket server (Python)
- `frontend_ws.html` - Interactive dashboard (HTML/JS)
- `deploy.sh` - Deployment and management script
