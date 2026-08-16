import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI + HTMX Todo Analytics App"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./todos.db")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
