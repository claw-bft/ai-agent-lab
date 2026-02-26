"""Sessions router"""
from typing import List
from fastapi import APIRouter, HTTPException
from app.models import SessionInfo, SessionDetail
from app.services import get_session_service

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("", response_model=List[SessionInfo])
async def list_sessions():
    """List all sessions"""
    service = get_session_service()
    return service.list_sessions()


@router.get("/{session_id}", response_model=SessionDetail)
async def get_session(session_id: str):
    """Get session by ID"""
    service = get_session_service()
    session = service.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    return session
