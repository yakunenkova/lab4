# SPA Salon API — Лабораторная работа №3

## Тема: Авторизация и аутентификация (JWT, OAuth2, Cookies)

---

## Краткое описание

RESTful API для управления услугами SPA-салона с системой аутентификации и авторизации. Реализовано на FastAPI с использованием PostgreSQL, SQLAlchemy, Alembic, JWT, bcrypt. В рамках лабораторной работы реализована регистрация и вход пользователей, выдача JWT-токенов через HttpOnly cookies, обновление токенов, управление сессиями (logout, logout-all), хеширование паролей и токенов, а также OAuth 2.0 авторизация через Яндекс ID.

---

## Функциональность (дополнение к ЛР №2)

- Регистрация пользователей (хеширование паролей bcrypt с уникальной солью)
- Аутентификация (вход) с выдачей JWT-токенов
- Access Token (15 минут) и Refresh Token (7 дней)
- Передача токенов через HttpOnly cookies (защита от XSS)
- Обновление пары токенов (refresh)
- Завершение сессии (logout) и всех сессий (logout-all)
- Хранение refresh токенов в БД в хешированном виде (bcrypt)
- Эндпоинт `/whoami` для проверки авторизации
- Защита ресурсов из ЛР №2 (только авторизованные пользователи)
- OAuth 2.0 авторизация через Яндекс ID

---

## Эндпоинты аутентификации

| Метод | Полный URL | Описание |
|-------|-----------|----------|
| POST | `http://localhost:8000/api/v1/auth/register` | Регистрация нового пользователя |
| POST | `http://localhost:8000/api/v1/auth/login` | Вход в систему (установка HttpOnly cookies) |
| POST | `http://localhost:8000/api/v1/auth/refresh` | Обновление пары токенов (access + refresh) |
| GET | `http://localhost:8000/api/v1/auth/whoami` | Проверка авторизации и получение данных пользователя |
| POST | `http://localhost:8000/api/v1/auth/logout` | Завершение текущей сессии |
| POST | `http://localhost:8000/api/v1/auth/logout-all` | Завершение всех сессий пользователя |
| GET | `http://localhost:8000/api/v1/auth/oauth/yandex` | Вход через Яндекс ID (OAuth 2.0) |
| GET | `http://localhost:8000/api/v1/auth/oauth/yandex/callback` | Callback для OAuth 2.0 |

---

## Примеры запросов

### Регистрация
```json
POST http://localhost:8000/api/v1/auth/register
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "Иван Петров"
}
```

### Логин
```json
POST http://localhost:8000/api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}
```
### Проверка авторизации
GET http://localhost:8000/api/v1/auth/whoami
### Обновление токенов
POST http://localhost:8000/api/v1/auth/refresh
### Выход
POST http://localhost:8000/api/v1/auth/logout
### Выход из всех устройств
POST http://localhost:8000/api/v1/auth/logout-all
### OAuth вход через Яндекс
GET http://localhost:8000/api/v1/auth/oauth/yandex


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


