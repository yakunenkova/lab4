from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "spa_db"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: str = "5432"
    PORT: int = 8000
    APP_NAME: str = "SPA Salon API"
    ENVIRONMENT: str = "development"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()