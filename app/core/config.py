# app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    ENV: str
    # any other values like REDIS_URL, ENV, etc.

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instantiate settings once for the app
settings = Settings()
