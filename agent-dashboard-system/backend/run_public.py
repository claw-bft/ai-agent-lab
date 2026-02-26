#!/usr/bin/env python3
import uvicorn
import sys
sys.path.insert(0, '/root/.openclaw/workspace/agent-dashboard-system/backend')
from app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
