from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    # API configuration
    google_api_key: str
    groq_api_key: str
    
    ingestion_model_name: str = "gemini-2.5-flash"
    chat_model_name: str = "llama-3.3-70b-versatile"
    
    # Vector DB
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection: str = "legal_docs"
    
    # Relational metadata (SQLite)
    sqlite_db_path: str = "storage/legal_data.db"
    
    # App Settings
    debug: bool = False
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate settings
settings = Settings()
