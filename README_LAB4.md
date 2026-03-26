# SPA Salon API — Лабораторная работа №4

Автоматизированное документирование REST API с использованием OpenAPI (Swagger)

---

## Краткое описание

RESTful API для управления услугами SPA-салона с системой аутентификации и авторизации. В рамках лабораторной работы настроена автоматическая документация API на основе спецификации OpenAPI с использованием встроенных средств FastAPI. Реализовано условное отключение документации в production-среде, аннотирование контроллеров и DTO, настройка схемы безопасности для JWT-токенов в HttpOnly cookies.

---

## Функциональность (дополнение к ЛР №2 и ЛР №3)

- Автоматическая генерация документации OpenAPI (Swagger UI, ReDoc)
- Условное отключение документации в production (по переменной `ENVIRONMENT`)
- Аннотирование эндпоинтов (summary, description, responses)
- Документирование DTO с описаниями полей и примерами
- Настройка схемы безопасности для HttpOnly cookies
- Маркировка защищенных эндпоинтов значком замка
- Тестирование защищенных эндпоинтов через Swagger UI

---

## Эндпоинты документации

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `http://localhost:8000/docs` | Swagger UI (интерактивная документация) |
| GET | `http://localhost:8000/redoc` | ReDoc (альтернативный интерфейс) |
| GET | `http://localhost:8000/openapi.json` | OpenAPI спецификация в формате JSON |

---

## Настройка документации

### Условное отключение в production

В файле `app/main.py` добавлена проверка переменной `ENVIRONMENT`:

```python
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    app.docs_url = None
    app.redoc_url = None
    app.openapi_url = None
```
## Переменные окружения

Создайте файл `.env` в корне проекта и скопируйте в него содержимое `.env.example`:

```env
# Database
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=spa_db
DB_HOST=localhost
DB_PORT=5432

# Application
PORT=8000
APP_NAME="SPA Salon API"
ENVIRONMENT=development

# JWT
JWT_ACCESS_SECRET=super_secret_access_key_change_in_prod
JWT_REFRESH_SECRET=super_secret_refresh_key_change_in_prod
JWT_ACCESS_EXPIRATION=15m
JWT_REFRESH_EXPIRATION=7d

# OAuth (опционально)
YANDEX_CLIENT_ID=
YANDEX_CLIENT_SECRET=
YANDEX_REDIRECT_URI=http://localhost:8000/api/v1/auth/oauth/yandex/callback
```

## Запуск проекта

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/yakunenkova/lab4.git
cd lab4
```
### 2. Создайте файл переменных окружения
```bash
cp .env.example .env
```
### 3. Запустите приложение
```bash
docker-compose up --build
```
## Автор
**Студент:** Якуненкова Полина
**Группа:** 020303-АИСа-о23