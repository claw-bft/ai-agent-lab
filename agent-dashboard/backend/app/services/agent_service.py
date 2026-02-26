"""Agent service for managing agent information"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from app.models import AgentInfo, AgentStatus
from app.config import get_settings
from app.services.session_service import get_session_service


class AgentService:
    """Service for agent data operations"""
    
    def __init__(self):
        self.settings = get_settings()
        self.skills_dir = Path(self.settings.SKILLS_DIR)
        self.agents_dir = Path("/root/.openclaw/agents")
    
    def list_agents(self) -> List[AgentInfo]:
        """List all agents and their status"""
        agents = []
        
        # Main agent
        main_agent = self._get_main_agent()
        if main_agent:
            agents.append(main_agent)
        
        # Subagents from agent directory
        if self.agents_dir.exists():
            for agent_dir in self.agents_dir.iterdir():
                if agent_dir.is_dir() and agent_dir.name != "main":
                    agent = self._get_subagent(agent_dir.name, agent_dir)
                    if agent:
                        agents.append(agent)
        
        return agents
    
    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent by ID"""
        agents = self.list_agents()
        for agent in agents:
            if agent.id == agent_id:
                return agent
        return None
    
    def _get_main_agent(self) -> Optional[AgentInfo]:
        """Get main agent information"""
        session_service = get_session_service()
        active_sessions = session_service.get_active_sessions_count()
        total_sessions = len(session_service.list_sessions())
        
        # Get skills
        skills = self._get_skills_list()
        
        # Determine status
        status = AgentStatus.IDLE if active_sessions == 0 else AgentStatus.BUSY
        
        return AgentInfo(
            id="main",
            name="Main Agent",
            description="Primary agent for handling user interactions",
            status=status,
            skills=skills,
            active_sessions=active_sessions,
            total_sessions=total_sessions,
            last_active=datetime.now(),
            capabilities=["chat", "tools", "skills", "cron", "subagents"]
        )
    
    def _get_subagent(self, agent_id: str, agent_dir: Path) -> Optional[AgentInfo]:
        """Get subagent information"""
        # Count sessions for this agent
        sessions_dir = agent_dir / "sessions"
        active_sessions = 0
        total_sessions = 0
        
        if sessions_dir.exists():
            for f in sessions_dir.glob("*.jsonl"):
                if not f.name.endswith(".lock"):
                    total_sessions += 1
            active_sessions = len(list(sessions_dir.glob("*.jsonl.lock")))
        
        # Determine status
        status = AgentStatus.IDLE if active_sessions == 0 else AgentStatus.BUSY
        
        # Try to read agent config if exists
        config_file = agent_dir / "config.json"
        name = agent_id
        description = None
        capabilities = []
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    name = config.get("name", agent_id)
                    description = config.get("description")
                    capabilities = config.get("capabilities", [])
            except Exception:
                pass
        
        return AgentInfo(
            id=agent_id,
            name=name,
            description=description or f"Subagent: {agent_id}",
            status=status,
            skills=[],
            active_sessions=active_sessions,
            total_sessions=total_sessions,
            last_active=datetime.now() if active_sessions > 0 else None,
            capabilities=capabilities or ["task_execution"]
        )
    
    def _get_skills_list(self) -> List[str]:
        """Get list of available skills"""
        skills = []
        if self.skills_dir.exists():
            for skill_dir in self.skills_dir.iterdir():
                if skill_dir.is_dir():
                    skills.append(skill_dir.name)
        return sorted(skills)
    
    def get_agent_stats(self) -> Dict[str, int]:
        """Get agent statistics"""
        agents = self.list_agents()
        return {
            "total": len(agents),
            "idle": sum(1 for a in agents if a.status == AgentStatus.IDLE),
            "busy": sum(1 for a in agents if a.status == AgentStatus.BUSY),
            "error": sum(1 for a in agents if a.status == AgentStatus.ERROR),
        }


# Singleton instance
_agent_service = None


def get_agent_service() -> AgentService:
    """Get agent service singleton"""
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service
