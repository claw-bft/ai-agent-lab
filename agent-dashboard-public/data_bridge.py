#!/usr/bin/env python3
"""
数据桥接服务
- 每秒扫描 OpenClaw sessions
- 写入静态 JSON 文件
- 由 Nginx 提供 HTTP 服务
"""

import json
import os
import glob
import time
from datetime import datetime
from pathlib import Path

# 配置
SESSIONS_DIR = "/root/.openclaw/agents/main/sessions/"
OUTPUT_DIR = "/root/.openclaw/workspace/agent-dashboard-public/data/"
SCAN_INTERVAL = 3  # 秒

def scan_sessions():
    """扫描所有会话"""
    sessions = []
    
    for jsonl_file in glob.glob(os.path.join(SESSIONS_DIR, "*.jsonl")):
        try:
            with open(jsonl_file, 'r') as f:
                first_line = f.readline()
                if not first_line:
                    continue
                    
                data = json.loads(first_line)
                session_id = os.path.basename(jsonl_file).replace('.jsonl', '')
                
                # 获取文件修改时间
                mtime = os.path.getmtime(jsonl_file)
                
                sessions.append({
                    "id": session_id,
                    "key": data.get("sessionKey", ""),
                    "displayName": data.get("displayName", ""),
                    "kind": data.get("kind", "unknown"),
                    "status": "active" if data.get("abortedLastRun") == False else "completed",
                    "updatedAt": data.get("updatedAt", 0),
                    "updatedAtFormatted": datetime.fromtimestamp(data.get("updatedAt", 0)/1000).isoformat() if data.get("updatedAt") else "",
                    "totalTokens": data.get("totalTokens", 0),
                    "model": data.get("model", "unknown"),
                    "lastChannel": data.get("lastChannel", ""),
                    "transcriptPath": data.get("transcriptPath", "")
                })
        except Exception as e:
            print(f"Error reading {jsonl_file}: {e}")
    
    # 按更新时间排序
    sessions.sort(key=lambda x: x["updatedAt"], reverse=True)
    return sessions

def get_stats(sessions):
    """生成统计信息"""
    total = len(sessions)
    active = len([s for s in sessions if s["status"] == "active"])
    completed = len([s for s in sessions if s["status"] == "completed"])
    
    total_tokens = sum(s.get("totalTokens", 0) for s in sessions)
    
    return {
        "totalSessions": total,
        "activeSessions": active,
        "completedSessions": completed,
        "totalTokens": total_tokens,
        "lastUpdate": datetime.now().isoformat(),
        "serverTime": int(time.time() * 1000)
    }

def main():
    """主循环"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"[{datetime.now().isoformat()}] 数据桥接服务启动")
    print(f"扫描目录: {SESSIONS_DIR}")
    print(f"输出目录: {OUTPUT_DIR}")
    
    while True:
        try:
            # 扫描数据
            sessions = scan_sessions()
            stats = get_stats(sessions)
            
            # 写入文件
            data = {
                "stats": stats,
                "sessions": sessions[:50],  # 只保留最近50个
                "generatedAt": datetime.now().isoformat()
            }
            
            output_file = os.path.join(OUTPUT_DIR, "dashboard.json")
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"[{datetime.now().isoformat()}] 更新完成: {len(sessions)} sessions, {stats['activeSessions']} active")
            
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] 错误: {e}")
        
        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    main()
