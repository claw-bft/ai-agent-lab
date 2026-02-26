from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "Agent Dashboard API"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Data paths
    SESSIONS_DIR: str = "/root/.openclaw/agents/main/sessions"
    SKILLS_DIR: str = "/root/.openclaw/skills"
    TASKS_DIR: str = "/root/.openclaw/shared/incoming"
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
