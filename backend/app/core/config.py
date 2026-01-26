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
    
    # LLM Configuration (supports multiple providers)
    LLM_PROVIDER: str = "groq"  # Options: openai, groq, ollama, local
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"  # or mistral, codellama, etc.
    
    # Database
    DATABASE_URL: str = "sqlite:///./atlas_ai.db"
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8501"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str = "change-this-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
