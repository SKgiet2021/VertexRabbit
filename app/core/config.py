
import os
from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "VertexRabbit"
    
    # Active Provider Selection
    # Options: "a4f", "openrouter", "groq"
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "a4f")
    
    # A4F Config (Default)
    A4F_API_KEY: str = os.getenv("A4F_API_KEY", "")
    A4F_BASE_URL: str = os.getenv("A4F_BASE_URL", "https://api.a4f.co/v1")
    A4F_MODEL: str = os.getenv("A4F_MODEL", "provider-7/claude-3-7-sonnet-20250219")
    
    # OpenRouter Config
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
    
    # Groq Config
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # A4F Config (Moved to top as default)
    
    # Legacy aliases for backward compatibility
    @property
    def VERTEX_API_KEY(self) -> str:
        return self.A4F_API_KEY
    
    @property
    def VERTEX_BASE_URL(self) -> str:
        return self.A4F_BASE_URL
    
    @property
    def VERTEX_MODEL(self) -> str:
        return self.A4F_MODEL

    # GitHub Config
    GITHUB_APP_ID: str = os.getenv("GITHUB_APP_ID", "")
    GITHUB_PRIVATE_KEY_PATH: str = os.getenv("GITHUB_PRIVATE_KEY_PATH", "")
    GITHUB_WEBHOOK_SECRET: str = os.getenv("GITHUB_WEBHOOK_SECRET", "")
    
    @property
    def GITHUB_PRIVATE_KEY(self) -> str:
        """Load private key from file if path is set"""
        if self.GITHUB_PRIVATE_KEY_PATH and os.path.exists(self.GITHUB_PRIVATE_KEY_PATH):
            with open(self.GITHUB_PRIVATE_KEY_PATH, "r") as f:
                return f.read()
        return ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()


