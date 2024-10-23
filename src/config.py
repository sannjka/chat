from typing import Optional
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: Optional[str] = None
    ALGORITHM: Optional[str] = None

    model_config = SettingsConfigDict(env_file='.env')

@lru_cache
def get_settings():
    return Settings()
