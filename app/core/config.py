from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "spa_db"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    PORT: int = 8000
    APP_NAME: str = "SPA Salon API"
    ENVIRONMENT: str = "development"

    # JWT
    JWT_ACCESS_SECRET: str = "super_secret_access_key_change_in_prod"
    JWT_REFRESH_SECRET: str = "super_secret_refresh_key_change_in_prod"
    JWT_ACCESS_EXPIRATION: str = "15m"
    JWT_REFRESH_EXPIRATION: str = "7d"

    # OAuth Yandex
    YANDEX_CLIENT_ID: str = ""
    YANDEX_CLIENT_SECRET: str = ""
    YANDEX_REDIRECT_URI: str = "http://localhost:8000/auth/yandex/callback"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()