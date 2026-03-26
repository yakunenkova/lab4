import os
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.api.v1.endpoints import services, auth

# Создание приложения
app = FastAPI(title="SPA Salon API", version="1.0.0")

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

# Настройка документации OpenAPI / Swagger

# Условное отключение документации в production
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    app.docs_url = None
    app.redoc_url = None
    app.openapi_url = None


# Настройка схемы безопасности для Swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="SPA Salon API",
        version="1.0.0",
        description="""
        API для управления SPA-салоном.

        ## Функциональность
        - Управление услугами (CRUD, пагинация, soft delete)
        - Аутентификация и авторизация (JWT, HttpOnly cookies)
        - Управление сессиями (logout, logout-all)

        ## Аутентификация
        Для доступа к защищенным эндпоинтам необходимо:
        1. Выполнить вход через `POST /api/v1/auth/login`
        2. После входа cookie с токенами устанавливаются автоматически
        3. Все последующие запросы к защищенным эндпоинтам будут содержать токены

        ## Защищенные эндпоинты
        - Все эндпоинты `/api/v1/auth` кроме `/register` и `/login`
        - Все эндпоинты `/api/v1/services`
        """,
        routes=app.routes,
    )

    # Добавление схемы безопасности для cookie-аутентификации
    openapi_schema["components"]["securitySchemes"] = {
        "CookieAuth": {
            "type": "apiKey",
            "in": "cookie",
            "name": "access_token",
            "description": "JWT токен в HttpOnly cookie. Для авторизации сначала выполните вход на /api/v1/auth/login"
        }
    }

    # Применение схемы безопасности ко всем защищенным эндпоинтам
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            # Исключаем эндпоинты регистрации и логина
            if "/auth/register" in path or "/auth/login" in path:
                continue
            # Добавляем требование авторизации для защищенных эндпоинтов
            openapi_schema["paths"][path][method]["security"] = [{"CookieAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Переопределяем метод openapi для использования кастомной схемы
app.openapi = custom_openapi