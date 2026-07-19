from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str
    GROQ_API_KEY: str
    HUGGINGFACE_TOKEN: str
    MAX_UPLOAD_SIZE: int = 10
    UPLOAD_DIR: str
    ACCESS_TOKEN_SECRET: str
    ACCESS_TOKEN_EXPIRE: int = 30
    REFRESH_TOKEN_SECRET: str
    REFRESH_TOKEN_EXPIRE: int = 10080
    APP_ENV: str = "development"

    class Config:
        env_file = '.env'

@lru_cache   # ensures that class Settings() instantiated once not on each file import - because .env is read once on startup
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
    