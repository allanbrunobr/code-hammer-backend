# app/core/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost/config_manager"

    class Config:
        env_file = ".env"

settings = Settings()
