"""Configuration management for the backend API."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    supabase_db_url: str

    # Supabase Auth (optional but recommended)
    # If your Supabase Auth tokens are HS256 signed, set supabase_jwt_secret.
    # If RS256 (JWKS), set supabase_project_url.
    supabase_project_url: str | None = None
    supabase_jwt_secret: str | None = None
    # Optional: used for remote token validation against Supabase Auth (works even when JWT secret isn't available)
    # This is safe to store server-side (it's a publishable/anon key), but do NOT use service_role here.
    supabase_anon_key: str | None = None
    
    # OpenAI
    openai_api_key: str
    openai_chat_model: str = "gpt-4o"
    openai_embed_model: str = "text-embedding-3-small"
    
    # HuggingFace RAG Configuration
    hf_embedding_model_name: str = "text-embedding-3-small"
    hf_chunker_version: str = "hf_chunker_v1"
    
    # API Configuration
    api_port: int = 8000
    api_host: str = "0.0.0.0"
    environment: str = "development"
    
    # Retrieval Configuration (deterministic)
    compute_top_k: int = 10
    k8s_top_k: int = 15
    hf_top_k: int = 5
    hf_chunk_top_k: int = 20  # Initial chunk retrieval before reranking
    
    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

