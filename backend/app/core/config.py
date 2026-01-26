"""
Configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Atlas AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # OpenAI
    OPENAI_API_KEY: str
    
    # Database
    DATABASE_URL: str = "sqlite:///./atlas_ai.db"
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8501"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str = "change-this-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
