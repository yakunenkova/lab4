import os
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.middleware.sessions import SessionMiddleware
from app.api.v1.endpoints import services, auth

# Загрузка переменных окружения из .env
from dotenv import load_dotenv

load_dotenv()

# Создание приложения
app = FastAPI(title="SPA Salon API", version="1.0.0")

# Добавление middleware для сессии (нужен для OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "your-super-secret-key-here"),
    session_cookie="session",
    max_age=3600
)

# Подключение роутеров
app.include_router(services.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")


# Корневые эндпоинты
@app.get("/")
async def root():
    return {"message": "SPA Salon API", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# ==================== Настройка документации ====================

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    app.docs_url = None
    app.redoc_url = None
    app.openapi_url = None


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="SPA Salon API",
        version="1.0.0",
        description="""
        API для управления SPA-салоном.

        ## Аутентификация
        - Логин: POST /api/v1/auth/login
        - Регистрация: POST /api/v1/auth/register
        - OAuth Яндекс: GET /api/v1/auth/oauth/yandex
        """,
        routes=app.routes,
    )

    # Добавление схемы безопасности для cookie-аутентификации
    openapi_schema["components"]["securitySchemes"] = {
        "CookieAuth": {
            "type": "apiKey",
            "in": "cookie",
            "name": "access_token",
            "description": "JWT токен в HttpOnly cookie"
        },
        "OAuth2": {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": "https://oauth.yandex.ru/authorize",
                    "tokenUrl": "https://oauth.yandex.ru/token",
                    "scopes": {}
                }
            },
            "description": "Вход через Яндекс ID"
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi