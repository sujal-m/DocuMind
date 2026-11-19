
import os
from pathlib import Path
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent  # DocuMind root
BASE_DIR = ROOT_DIR

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server Settings
    BASE_DIR: str = str(ROOT_DIR)
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Storage Paths
    DATA_DIR: str = str(ROOT_DIR / "backend" / "data")
    UPLOAD_DIR: str = str(ROOT_DIR / "backend" / "data" / "uploads")
    VECTOR_DIR: str = str(ROOT_DIR / "backend" / "data" / "vector")
    DATABASE_URL: str = f"sqlite:///{ROOT_DIR}/backend/data/documind.db"

    # LLM Settings
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.1-flash-lite"
    FALLBACK_MODELS: List[str] = ["gemini-3.1-flash-lite", "gemini-3.8-flash", "gemini-flash-latest"]

    # Embeddings & FAISS
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    LOCAL_MODEL_DIR: str = str(ROOT_DIR / "backend" / "data" / "models" / "all-MiniLM-L6-v2")
    EMBEDDING_DIMENSION: int = 384
    DEFAULT_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.35

    # Chunking & Files
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    MAX_UPLOAD_SIZE_MB: int = 50

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            import json
            try:
                return json.loads(v)
            except Exception:
                return ["*"]
        return v

settings = Settings()

# Ensure storage directories exist
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.VECTOR_DIR, exist_ok=True)
