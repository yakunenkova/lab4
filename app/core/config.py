import os
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/spa_db"

    # Application
    PORT: int = 8000
    APP_NAME: str = "SPA Salon API"
    ENVIRONMENT: str = "development"

    # JWT
    JWT_ACCESS_SECRET: str = "super_secret_access_key_change_in_prod"
    JWT_REFRESH_SECRET: str = "super_secret_refresh_key_change_in_prod"
    JWT_ACCESS_EXPIRATION: int = 15  # minutes
    JWT_REFRESH_EXPIRATION: int = 7 * 24 * 60  # minutes (7 days)

    # Session (для OAuth)
    SESSION_SECRET: str = "your_session_secret_key_here"

    # OAuth Yandex
    YANDEX_CLIENT_ID: str = "2d625c05258d4ca0ac07c74f0d6f6954"
    YANDEX_CLIENT_SECRET: str = "558ee78782884857aefa1eea025a2ff7"
    YANDEX_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/oauth/yandex/callback"
    YANDEX_AUTH_URL: str = "https://oauth.yandex.ru/authorize"
    YANDEX_TOKEN_URL: str = "https://oauth.yandex.ru/token"
    YANDEX_USER_INFO_URL: str = "https://login.yandex.ru/info"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()