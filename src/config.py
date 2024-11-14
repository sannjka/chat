from typing import Optional
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: Optional[str] = None
    ALGORITHM: Optional[str] = None

    DB_HOST: Optional[str] = None
    DB_PORT: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    TG_TOKEN: Optional[str] = None
    CELERY_BROKER: Optional[str] = None

    model_config = SettingsConfigDict(env_file='.env')

@lru_cache
def get_settings():
    return Settings()

def get_db_url():
    settings = get_settings()
    return (f'postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@'
            f'{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}')

def get_test_db_url():
    settings = get_settings()
    return (f'postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@'
            f'{settings.DB_HOST}:{settings.DB_PORT}/test_chat_db')
