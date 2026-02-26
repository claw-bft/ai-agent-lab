"""Agents router"""
from typing import List
from fastapi import APIRouter, HTTPException
from app.models import AgentInfo
from app.services import get_agent_service

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("", response_model=List[AgentInfo])
async def list_agents():
    """List all agents"""
    service = get_agent_service()
    return service.list_agents()


@router.get("/{agent_id}", response_model=AgentInfo)
async def get_agent(agent_id: str):
    """Get agent by ID"""
    service = get_agent_service()
    agent = service.get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    return agent
