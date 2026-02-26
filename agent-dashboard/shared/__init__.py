"""
OpenClaw Dashboard 数据提供模块

为Dashboard Frontend和Backend提供统一的数据接口

使用示例:
    from data_provider import get_sessions, get_tasks, get_agents, get_stats
    
    # 获取会话列表
    sessions = get_sessions(limit=10)
    
    # 获取Cron任务
    tasks = get_tasks()
    
    # 获取可用Agent
    agents = get_agents()
    
    # 获取统计指标
    stats = get_stats()
"""

from .data_provider import (
    get_sessions,
    get_session_by_id,
    get_tasks,
    get_task_by_id,
    get_agents,
    get_agent_by_id,
    get_stats,
    get_recent_activity,
    get_token_usage_by_day,
    SessionInfo,
    CronTask,
    AgentSkill,
    DashboardStats,
)

__all__ = [
    "get_sessions",
    "get_session_by_id",
    "get_tasks",
    "get_task_by_id",
    "get_agents",
    "get_agent_by_id",
    "get_stats",
    "get_recent_activity",
    "get_token_usage_by_day",
    "SessionInfo",
    "CronTask",
    "AgentSkill",
    "DashboardStats",
]
