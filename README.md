# SPA Salon API - Лабораторная работа №3

RESTful API для управления услугами SPA-салона с системой аутентификации и авторизации. Реализовано на FastAPI с использованием PostgreSQL, SQLAlchemy, Alembic, JWT, bcrypt.

## Функциональность (дополнение к ЛР №2)

- Регистрация пользователей (хеширование паролей bcrypt)
- Аутентификация (вход) с выдачей JWT-токенов
- Access Token (15 минут) и Refresh Token (7 дней)
- Передача токенов через HttpOnly cookies
- Обновление пары токенов (refresh)
- Завершение сессии (logout) и всех сессий (logout-all)
- Хранение refresh токенов в БД в хешированном виде
- Эндпоинт `/whoami` для проверки авторизации
- Защита ресурсов из ЛР №2 (только авторизованные пользователи)

## Эндпоинты аутентификации
| Метод | Полный URL | Описание |
|-------|-----------|----------|
| POST | `http://localhost:8000/api/v1/auth/register` | Регистрация нового пользователя |
| POST | `http://localhost:8000/api/v1/auth/login` | Вход в систему (установка HttpOnly cookies) |
| POST | `http://localhost:8000/api/v1/auth/refresh` | Обновление пары токенов (access + refresh) |
| GET | `http://localhost:8000/api/v1/auth/whoami` | Проверка авторизации и получение данных пользователя |
| POST | `http://localhost:8000/api/v1/auth/logout` | Завершение текущей сессии |
| POST | `http://localhost:8000/api/v1/auth/logout-all` | Завершение всех сессий пользователя |

## Примеры запросов

### Регистрация
```bash
POST `http://localhost:8000/api/v1/auth/register`
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "Иван Петров"
}
```

### Логин
```bash
POST `http://localhost:8000/api/v1/auth/login`
{
  "email": "user@example.com",
  "password": "password123"
}
```
### Проверка авторизации
```bash
GET `http://localhost:8000/api/v1/auth/whoami`
```
### Обновление токенов
```bash
POST `http://localhost:8000/api/v1/auth/refresh`
```
### Выход
```bash
POST `http://localhost:8000/api/v1/auth/logout`
```
### Выход из всех устройств
```bash
POST `http://localhost:8000/api/v1/auth/logout-all`
```
## Безопасность

| Механизм | Реализация |
|----------|------------|
| Хеширование паролей | bcrypt с уникальной солью |
| Хранение токенов в БД | token_hash (bcrypt) |
| Передача токенов | HttpOnly cookies (защита от XSS) |
| Отзыв токенов | is_revoked в таблице refresh_tokens |
| Access Token | 15 минут |
| Refresh Token | 7 дней |

---

## Модели данных

### User (пользователь)

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Уникальный идентификатор |
| email | String | Email пользователя (уникальный) |
| password_hash | String | Хеш пароля (bcrypt) |
| full_name | String | Полное имя |
| phone | String | Телефон (опционально) |
| is_active | Boolean | Активен ли пользователь |
| created_at | DateTime | Дата регистрации |

### RefreshToken (токен обновления)

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Уникальный идентификатор |
| user_id | Integer | Внешний ключ к пользователю |
| token_hash | String | Хеш refresh токена (bcrypt) |
| expires_at | DateTime | Срок действия |
| is_revoked | Boolean | Отозван ли токен |
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
git clone https://github.com/yakunenkova/lab3.git
cd lab3
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