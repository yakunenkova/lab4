# SPA Salon API

RESTful API для управления услугами SPA-салона. Реализовано на FastAPI с использованием PostgreSQL, SQLAlchemy, Alembic.

## Функциональность

- CRUD операции для услуг (создание, чтение, обновление, удаление)
- Пагинация списка услуг
- Мягкое удаление (soft delete)
- Валидация данных
- Автоматическая документация Swagger UI

## Запуск через Docker

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/yakunenkova/lab2.git
cd lab2
```

### 2. Создайте файл переменных окружения
```bash
cp .env.example .env
```
### 3. Запустите приложение
```bash
docker-compose up --build
```

##  Локальный запуск (без Docker)

### 1. Создать виртуальное окружение
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Установить зависимости
```bash
pip install -r requirements.txt
```
### 3. Применить миграции
```bash
alembic upgrade head
```
### 4. Запустить сервер
```bash
uvicorn app.main:app --reload
```

## Переменные окружения (`.env.example`)

```env
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=spa_db
DB_HOST=postgres
DB_PORT=5432
PORT=8000
APP_NAME="SPA Salon API"
ENVIRONMENT=development
```

## API Эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/v1/services?page=1&limit=10` | Получить список услуг (с пагинацией) |
| GET | `/api/v1/services/{id}` | Получить услугу по ID |
| POST | `/api/v1/services` | Создать новую услугу |
| PUT | `/api/v1/services/{id}` | Полностью обновить услугу |
| PATCH | `/api/v1/services/{id}` | Частично обновить услугу |
| DELETE | `/api/v1/services/{id}` | Мягкое удаление услуги |

### Параметры пагинации

| Параметр | Значение по умолчанию | Допустимый диапазон |
|----------|----------------------|---------------------|
| `page` | 1 | от 1 и выше |
| `limit` | 10 | от 1 до 100 |

## Миграции базы данных

```bash
# Создать новую миграцию
alembic revision --autogenerate -m "описание"

# Применить миграции
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1
```

## Автор

**Студент:** Якуненкова Полина
**Группа:** 020303-АИСа-о23 
