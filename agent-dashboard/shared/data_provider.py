#!/usr/bin/env python3
"""
OpenClaw Dashboard 数据提供模块
为Frontend和Backend提供统一的数据接口
"""

from __future__ import annotations

import json
import os
import glob
import subprocess
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


# ============== 配置 ==============
SESSIONS_DIR = Path("/root/.openclaw/agents/main/sessions")
SKILLS_DIR = Path("/root/.openclaw/workspace/skills")
OPENCLAW_BIN = "openclaw"


# ============== 数据模型 ==============
@dataclass
class SessionInfo:
    """会话信息"""
    id: str
    status: str  # active, completed, error, deleted
    start_time: Optional[str]
    end_time: Optional[str]
    duration_seconds: Optional[float]
    total_tokens: int
    input_tokens: int
    output_tokens: int
    message_count: int
    model: str
    provider: str
    has_error: bool
    is_deleted: bool
    file_size: int


@dataclass
class CronTask:
    """Cron任务信息"""
    id: str
    name: str
    agent_id: str
    enabled: bool
    schedule: str
    timezone: str
    next_run: Optional[str]
    last_run: Optional[str]
    last_status: Optional[str]  # success, error, running
    last_duration_ms: Optional[int]
    last_error: Optional[str]
    consecutive_errors: int
    session_target: str
    timeout_seconds: int


@dataclass
class AgentSkill:
    """Agent/技能信息"""
    id: str
    name: str
    description: str
    path: str
    has_skill_md: bool
    created_at: Optional[str]
    modified_at: Optional[str]


@dataclass
class DashboardStats:
    """仪表盘统计指标"""
    total_sessions: int
    active_sessions: int
    completed_sessions: int
    error_sessions: int
    total_tokens_consumed: int
    avg_session_duration: float
    total_tasks: int
    enabled_tasks: int
    error_tasks: int
    total_agents: int
    success_rate: float  # 百分比


# ============== Session 数据读取 ==============
def parse_session_file(file_path: Path) -> Optional[SessionInfo]:
    """解析单个会话文件"""
    try:
        file_name = file_path.name
        is_deleted = ".deleted." in file_name
        is_lock = file_name.endswith(".lock")
        
        if is_lock:
            return None
        
        # 提取会话ID
        if is_deleted:
            session_id = file_name.split(".jsonl.deleted.")[0]
        else:
            session_id = file_name.replace(".jsonl", "")
        
        file_size = file_path.stat().st_size
        
        # 解析JSONL文件
        messages = []
        session_meta = {}
        total_tokens = 0
        input_tokens = 0
        output_tokens = 0
        has_error = False
        start_time = None
        end_time = None
        model = "unknown"
        provider = "unknown"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    msg_type = data.get("type", "")
                    
                    if msg_type == "session":
                        session_meta = data
                        start_time = data.get("timestamp")
                    elif msg_type == "message":
                        messages.append(data)
                        msg_data = data.get("message", {})
                        usage = msg_data.get("usage", {})
                        if usage:
                            total_tokens += usage.get("totalTokens", 0)
                            input_tokens += usage.get("input", 0)
                            output_tokens += usage.get("output", 0)
                        
                        # 检测错误
                        if msg_data.get("role") == "assistant":
                            content = msg_data.get("content", [])
                            for item in content:
                                if isinstance(item, dict) and item.get("type") == "text":
                                    text = item.get("text", "")
                                    if "error" in text.lower() or "exception" in text.lower():
                                        has_error = True
                                        
                    elif msg_type == "model_change":
                        model = data.get("modelId", model)
                        provider = data.get("provider", provider)
                        
                except json.JSONDecodeError:
                    continue
        
        # 计算结束时间和状态
        if messages:
            last_msg = messages[-1]
            end_time = last_msg.get("timestamp")
        
        # 判断状态
        if is_deleted:
            status = "deleted"
        elif file_path.with_suffix(".jsonl.lock").exists():
            status = "active"
        elif has_error:
            status = "error"
        else:
            status = "completed"
        
        # 计算持续时间
        duration = None
        if start_time and end_time:
            try:
                start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                duration = (end - start).total_seconds()
            except:
                pass
        
        return SessionInfo(
            id=session_id,
            status=status,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            total_tokens=total_tokens,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            message_count=len(messages),
            model=model,
            provider=provider,
            has_error=has_error,
            is_deleted=is_deleted,
            file_size=file_size
        )
        
    except Exception as e:
        print(f"Error parsing session {file_path}: {e}")
        return None


def get_sessions(limit: int = 100, include_deleted: bool = False) -> List[Dict[str, Any]]:
    """
    获取会话列表
    
    Args:
        limit: 最大返回数量
        include_deleted: 是否包含已删除的会话
    
    Returns:
        会话信息列表
    """
    sessions = []
    
    if not SESSIONS_DIR.exists():
        return sessions
    
    # 获取所有jsonl文件
    pattern = "*.jsonl" if include_deleted else "*.jsonl"
    files = list(SESSIONS_DIR.glob(pattern))
    
    # 过滤掉.lock文件
    files = [f for f in files if not f.name.endswith(".lock")]
    
    # 按修改时间排序（最新的在前）
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    for file_path in files[:limit]:
        session = parse_session_file(file_path)
        if session:
            sessions.append(asdict(session))
    
    return sessions


def get_session_by_id(session_id: str) -> Optional[Dict[str, Any]]:
    """获取单个会话详情"""
    # 尝试查找文件
    file_path = SESSIONS_DIR / f"{session_id}.jsonl"
    if not file_path.exists():
        # 尝试查找已删除的文件
        deleted_files = list(SESSIONS_DIR.glob(f"{session_id}.jsonl.deleted.*"))
        if deleted_files:
            file_path = deleted_files[0]
        else:
            return None
    
    session = parse_session_file(file_path)
    return asdict(session) if session else None


# ============== Cron 任务读取 ==============
def get_tasks() -> List[Dict[str, Any]]:
    """
    获取所有Cron任务
    
    Returns:
        任务信息列表
    """
    tasks = []
    
    try:
        result = subprocess.run(
            [OPENCLAW_BIN, "cron", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # 尝试解析JSON输出
        stdout = result.stdout.strip()
        
        # 查找JSON部分（可能在警告信息之后）
        json_start = stdout.find('{')
        if json_start >= 0:
            json_str = stdout[json_start:]
            try:
                data = json.loads(json_str)
                jobs = data.get("jobs", [])
            except json.JSONDecodeError:
                # 解析文本输出
                return _parse_cron_text_output(stdout)
        else:
            # 解析文本输出
            return _parse_cron_text_output(stdout)
        
        for job in jobs:
            schedule = job.get("schedule", {})
            state = job.get("state", {})
            payload = job.get("payload", {})
            
            # 转换时间戳
            next_run = None
            last_run = None
            
            next_run_ms = state.get("nextRunAtMs")
            last_run_ms = state.get("lastRunAtMs")
            
            if next_run_ms:
                try:
                    next_run = datetime.fromtimestamp(
                        next_run_ms / 1000, 
                        tz=timezone.utc
                    ).isoformat()
                except (ValueError, OSError, OverflowError):
                    next_run = None
            
            if last_run_ms:
                try:
                    last_run = datetime.fromtimestamp(
                        last_run_ms / 1000,
                        tz=timezone.utc
                    ).isoformat()
                except (ValueError, OSError, OverflowError):
                    last_run = None
            
            task = CronTask(
                id=job.get("id", ""),
                name=job.get("name", ""),
                agent_id=job.get("agentId", ""),
                enabled=job.get("enabled", False),
                schedule=f"{schedule.get('expr', '')} @ {schedule.get('tz', '')}",
                timezone=schedule.get("tz", "UTC"),
                next_run=next_run,
                last_run=last_run,
                last_status=state.get("lastStatus"),
                last_duration_ms=state.get("lastDurationMs"),
                last_error=state.get("lastError"),
                consecutive_errors=state.get("consecutiveErrors", 0),
                session_target=job.get("sessionTarget", ""),
                timeout_seconds=payload.get("timeoutSeconds", 300)
            )
            tasks.append(asdict(task))
            
    except Exception as e:
        print(f"Error fetching cron tasks: {e}")
    
    return tasks


def _parse_cron_text_output(output: str) -> List[Dict[str, Any]]:
    """解析cron list的文本输出（备用方案）"""
    tasks = []
    lines = output.strip().split("\n")
    
    # 查找表头行
    header_idx = -1
    for i, line in enumerate(lines):
        if "ID" in line and "Name" in line and "Schedule" in line:
            header_idx = i
            break
    
    if header_idx < 0:
        return tasks
    
    # 解析数据行（表头下一行）
    for line in lines[header_idx + 1:]:
        line = line.strip()
        if not line:
            continue
        
        # 按固定宽度解析（根据表头对齐）
        # ID: 0-36, Name: 37-61, Schedule: 62-94, Next: 95-105, Last: 106-116, Status: 117-126, Target: 127-136, Agent: 137+
        if len(line) < 100:
            continue
            
        task_id = line[0:36].strip()
        name = line[37:62].strip()
        schedule = line[62:94].strip()
        next_run = line[95:105].strip()
        last_run = line[106:116].strip()
        status = line[117:126].strip()
        target = line[127:137].strip()
        agent = line[138:].strip() if len(line) > 138 else "main"
        
        if not task_id or task_id == "ID":
            continue
        
        # 清理状态
        status = status.lower()
        if status not in ["success", "error", "running", "pending"]:
            status = "unknown"
        
        tasks.append({
            "id": task_id,
            "name": name,
            "schedule": schedule,
            "next_run": next_run if next_run != "-" else None,
            "last_run": last_run if last_run != "-" else None,
            "last_status": status,
            "enabled": True,
            "agent_id": agent,
            "timezone": "Asia/Shanghai" if "Asia/Shanghai" in schedule else "UTC",
            "consecutive_errors": 0,
            "session_target": target,
            "timeout_seconds": 300,
            "last_duration_ms": None,
            "last_error": None
        })
    
    return tasks


def get_task_by_id(task_id: str) -> Optional[Dict[str, Any]]:
    """获取单个任务详情"""
    tasks = get_tasks()
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


# ============== 技能目录扫描 ==============
def get_agents() -> List[Dict[str, Any]]:
    """
    扫描并获取所有可用Agent/技能
    
    Returns:
        Agent/技能信息列表
    """
    agents = []
    
    if not SKILLS_DIR.exists():
        return agents
    
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        
        skill_md = skill_dir / "SKILL.md"
        has_skill_md = skill_md.exists()
        
        # 解析SKILL.md获取名称和描述
        name = skill_dir.name
        description = ""
        
        if has_skill_md:
            try:
                with open(skill_md, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 尝试从YAML frontmatter提取
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 2:
                            import yaml
                            try:
                                meta = yaml.safe_load(parts[1])
                                if meta:
                                    name = meta.get("name", name)
                                    description = meta.get("description", "")
                            except:
                                pass
                    
                    # 如果没有描述，取第一段文字
                    if not description:
                        lines = content.split("\n")
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith("#") and not line.startswith("-"):
                                description = line[:200]
                                break
            except Exception as e:
                print(f"Error reading {skill_md}: {e}")
        
        stat = skill_dir.stat()
        
        agent = AgentSkill(
            id=skill_dir.name,
            name=name,
            description=description,
            path=str(skill_dir),
            has_skill_md=has_skill_md,
            created_at=datetime.fromtimestamp(stat.st_ctime).isoformat(),
            modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat()
        )
        agents.append(asdict(agent))
    
    # 按名称排序
    agents.sort(key=lambda x: x["name"])
    return agents


def get_agent_by_id(agent_id: str) -> Optional[Dict[str, Any]]:
    """获取单个Agent详情"""
    agents = get_agents()
    for agent in agents:
        if agent["id"] == agent_id:
            return agent
    return None


# ============== 统计指标 ==============
def get_stats() -> Dict[str, Any]:
    """
    生成仪表盘统计指标
    
    Returns:
        统计指标字典
    """
    # 获取所有会话（包括已删除）
    sessions = get_sessions(limit=1000, include_deleted=True)
    tasks = get_tasks()
    agents = get_agents()
    
    # 会话统计
    total_sessions = len(sessions)
    active_sessions = sum(1 for s in sessions if s["status"] == "active")
    completed_sessions = sum(1 for s in sessions if s["status"] == "completed")
    error_sessions = sum(1 for s in sessions if s["status"] == "error")
    
    # Token统计
    total_tokens = sum(s["total_tokens"] for s in sessions)
    
    # 平均持续时间（仅计算已完成的）
    completed_with_duration = [
        s["duration_seconds"] for s in sessions 
        if s["duration_seconds"] is not None
    ]
    avg_duration = sum(completed_with_duration) / len(completed_with_duration) if completed_with_duration else 0
    
    # 任务统计
    total_tasks = len(tasks)
    enabled_tasks = sum(1 for t in tasks if t.get("enabled", False))
    error_tasks = sum(1 for t in tasks if t.get("last_status") == "error")
    
    # 成功率计算（基于最近30个非删除会话）
    recent_sessions = [s for s in sessions if not s["is_deleted"]][:30]
    if recent_sessions:
        success_count = sum(1 for s in recent_sessions if s["status"] == "completed" and not s["has_error"])
        success_rate = (success_count / len(recent_sessions)) * 100
    else:
        success_rate = 0
    
    stats = DashboardStats(
        total_sessions=total_sessions,
        active_sessions=active_sessions,
        completed_sessions=completed_sessions,
        error_sessions=error_sessions,
        total_tokens_consumed=total_tokens,
        avg_session_duration=round(avg_duration, 2),
        total_tasks=total_tasks,
        enabled_tasks=enabled_tasks,
        error_tasks=error_tasks,
        total_agents=len(agents),
        success_rate=round(success_rate, 2)
    )
    
    return asdict(stats)


# ============== 辅助函数 ==============
def get_recent_activity(hours: int = 24) -> List[Dict[str, Any]]:
    """获取最近的活动记录"""
    sessions = get_sessions(limit=100, include_deleted=False)
    
    cutoff = datetime.now(timezone.utc).timestamp() - (hours * 3600)
    recent = []
    
    for session in sessions:
        if session["start_time"]:
            try:
                start = datetime.fromisoformat(session["start_time"].replace('Z', '+00:00'))
                if start.timestamp() > cutoff:
                    recent.append(session)
            except:
                pass
    
    return recent


def get_token_usage_by_day(days: int = 7) -> List[Dict[str, Any]]:
    """获取每日Token使用量统计"""
    sessions = get_sessions(limit=1000, include_deleted=False)
    
    from collections import defaultdict
    daily_usage = defaultdict(lambda: {"input": 0, "output": 0, "total": 0, "count": 0})
    
    for session in sessions:
        if session["start_time"]:
            try:
                start = datetime.fromisoformat(session["start_time"].replace('Z', '+00:00'))
                date_key = start.strftime("%Y-%m-%d")
                daily_usage[date_key]["input"] += session["input_tokens"]
                daily_usage[date_key]["output"] += session["output_tokens"]
                daily_usage[date_key]["total"] += session["total_tokens"]
                daily_usage[date_key]["count"] += 1
            except:
                pass
    
    # 转换为列表并排序
    result = [
        {"date": date, **data}
        for date, data in daily_usage.items()
    ]
    result.sort(key=lambda x: x["date"], reverse=True)
    return result[:days]


# ============== 主函数（测试用） ==============
if __name__ == "__main__":
    print("=" * 60)
    print("OpenClaw Dashboard Data Provider")
    print("=" * 60)
    
    print("\n📊 Stats:")
    stats = get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n📝 Recent Sessions (5):")
    sessions = get_sessions(limit=5)
    for s in sessions:
        print(f"  - {s['id'][:8]}... | {s['status']} | {s['total_tokens']} tokens")
    
    print("\n⏰ Cron Tasks:")
    tasks = get_tasks()
    for t in tasks:
        print(f"  - {t['name']} | {t['schedule']} | {t['last_status']}")
    
    print("\n🤖 Available Agents:")
    agents = get_agents()
    for a in agents:
        print(f"  - {a['name']}: {a['description'][:50]}...")
    
    print("\n📈 Token Usage by Day:")
    usage = get_token_usage_by_day(7)
    for u in usage:
        print(f"  {u['date']}: {u['total']} tokens ({u['count']} sessions)")
