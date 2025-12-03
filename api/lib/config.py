from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # JWT Settings
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # API Keys
    pinecone_api_key: Optional[str] = os.getenv("PINECONE_API_KEY")
    google_api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
    sarvam_api_key: Optional[str] = os.getenv("SARVAM_API_KEY")
    
    # Embedding Configuration
    embedding_dim: int = int(os.getenv("EMBEDDING_DIM", "768"))  # For embedding-001 model
    
    # Database (for future use if needed)
    database_url: Optional[str] = os.getenv("DATABASE_URL")
    
    # Environment
    environment: Optional[str] = os.getenv("ENVIRONMENT", "development")
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env

settings = Settings()