# Agent Dashboard System - 部署指南

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Dashboard System                    │
├─────────────────────────────────────────────────────────────┤
│  Frontend (React/Vanilla)  │  Port: 8080                     │
│  - 实时状态显示              │  - 深色主题                     │
│  - WebSocket连接            │  - 专业UI                       │
├─────────────────────────────────────────────────────────────┤
│  Backend (FastAPI)         │  Port: 8000                     │
│  - REST API                │  - /api/sessions               │
│  - WebSocket推送            │  - /api/stats                  │
│  - 数据持久化(SQLite)        │  - /ws                         │
├─────────────────────────────────────────────────────────────┤
│  Monitor (Python)          │  Background Process            │
│  - 每秒扫描sessions目录      │  - 历史数据记录                 │
│  - 状态变化检测              │  - SQLite存储                   │
└─────────────────────────────────────────────────────────────┘
```

## 目录结构

```
agent-dashboard-system/
├── backend/                 # FastAPI后端服务
│   ├── main.py             # 主入口
│   ├── services/           # 服务模块
│   │   ├── __init__.py
│   │   ├── data_store.py   # 数据存储
│   │   ├── session_scanner.py  # 会话扫描
│   │   └── websocket_manager.py # WebSocket管理
│   ├── requirements.txt
│   └── venv/               # Python虚拟环境
├── monitor/                # 监控进程
│   ├── monitor.py          # 主程序
│   ├── requirements.txt
│   └── venv/               # Python虚拟环境
├── frontend/               # 前端
│   └── index.html          # 单页面应用
├── logs/                   # 日志目录
│   ├── backend.log
│   ├── monitor.log
│   ├── frontend.log
│   └── *.pid               # PID文件
├── start.sh                # 启动脚本
└── README.md               # 本文件
```

## 快速开始

### 1. 一键启动

```bash
cd /root/.openclaw/workspace/agent-dashboard-system
./start.sh start
```

这将启动所有服务:
- Backend: http://localhost:8000
- Frontend: http://localhost:8080
- WebSocket: ws://localhost:8000/ws

### 2. 查看状态

```bash
./start.sh status
```

### 3. 查看日志

```bash
./start.sh logs backend    # 后端日志
./start.sh logs monitor    # 监控进程日志
./start.sh logs frontend   # 前端日志
```

### 4. 停止服务

```bash
./start.sh stop
```

### 5. 重启服务

```bash
./start.sh restart
```

## API文档

### REST API

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/stats` | GET | 系统统计信息 |
| `/api/sessions` | GET | 所有活跃会话 |
| `/api/sessions/{id}` | GET | 会话详情 |
| `/api/tasks` | GET | 所有任务 |
| `/api/agents` | GET | Agent注册表 |
| `/health` | GET | 健康检查 |

### WebSocket

连接: `ws://localhost:8000/ws`

消息类型:
- `init` - 初始数据
- `session_new` - 新会话
- `session_update` - 会话更新
- `session_closed` - 会话关闭
- `heartbeat` - 心跳

## 配置

### 修改端口

编辑 `start.sh` 文件中的端口配置:

```bash
BACKEND_PORT=8000
FRONTEND_PORT=8080
```

### 修改扫描间隔

编辑 `monitor/monitor.py`:

```python
SCAN_INTERVAL = 1.0  # 秒
```

### 数据库位置

默认: `~/.openclaw/agent_dashboard.db`

可在 `backend/services/data_store.py` 和 `monitor/monitor.py` 中修改。

## 手动安装依赖

如果自动安装失败，可以手动安装:

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Monitor
cd ../monitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 手动启动

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python3 main.py

# Terminal 2 - Monitor
cd monitor
source venv/bin/activate
python3 monitor.py

# Terminal 3 - Frontend
cd frontend
python3 -m http.server 8080
```

## 系统要求

- Python 3.8+
- Linux/macOS (Windows需要WSL)
- 磁盘空间: ~100MB
- 内存: ~50MB运行时

## 故障排除

### 端口被占用

```bash
# 查找占用端口的进程
lsof -Pi :8000 -sTCP:LISTEN

# 终止进程
kill -9 <PID>
```

### 权限问题

```bash
chmod +x start.sh
```

### 依赖安装失败

```bash
# 更新pip
pip install --upgrade pip

# 手动安装
pip install fastapi uvicorn websockets aiofiles aiohttp
```

## 扩展开发

### 添加新的API端点

在 `backend/main.py` 中添加:

```python
@app.get("/api/custom")
async def custom_endpoint():
    return {"data": "custom"}
```

### 添加新的监控指标

在 `monitor/monitor.py` 的 `_read_session` 方法中添加:

```python
# 读取自定义文件
custom_file = session_dir / "custom.json"
if custom_file.exists():
    # 解析并添加到info
    pass
```

### 前端自定义

直接编辑 `frontend/index.html`，修改样式或添加新组件。

## 生产部署

### 使用systemd

创建 `/etc/systemd/system/agent-dashboard.service`:

```ini
[Unit]
Description=Agent Dashboard
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/root/.openclaw/workspace/agent-dashboard-system
ExecStart=/root/.openclaw/workspace/agent-dashboard-system/start.sh start
ExecStop=/root/.openclaw/workspace/agent-dashboard-system/start.sh stop
Restart=always

[Install]
WantedBy=multi-user.target
```

启用服务:

```bash
sudo systemctl enable agent-dashboard
sudo systemctl start agent-dashboard
sudo systemctl status agent-dashboard
```

### 使用Docker (可选)

创建 `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt /app/backend/
COPY monitor/requirements.txt /app/monitor/

RUN pip install -r backend/requirements.txt
RUN pip install -r monitor/requirements.txt

COPY . /app

EXPOSE 8000 8080

CMD ["./start.sh", "start"]
```

## 数据备份

数据库文件位于 `~/.openclaw/agent_dashboard.db`，定期备份此文件。

```bash
# 备份
cp ~/.openclaw/agent_dashboard.db ~/.openclaw/agent_dashboard.db.backup

# 恢复
cp ~/.openclaw/agent_dashboard.db.backup ~/.openclaw/agent_dashboard.db
```

## 许可证

MIT License
