import bcrypt
import jwt
import secrets
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, Response

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.auth import LoginRequest, RegisterRequest
from app.core.config import settings


class AuthService:

    # ==================== Хеширование ====================
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def hash_token(token: str) -> str:
        """Хеширование токена для хранения в БД (обрезка до 72 байт)"""
        token_bytes = token.encode('utf-8')[:72]
        return bcrypt.hashpw(token_bytes, bcrypt.gensalt()).decode('utf-8')

    # ==================== JWT ====================
    @staticmethod
    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_EXPIRATION)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, settings.JWT_ACCESS_SECRET, algorithm="HS256")

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_REFRESH_EXPIRATION)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.JWT_REFRESH_SECRET, algorithm="HS256")

    @staticmethod
    def verify_access_token(token: str) -> Optional[int]:
        try:
            payload = jwt.decode(token, settings.JWT_ACCESS_SECRET, algorithms=["HS256"])
            user_id = payload.get("sub")
            if payload.get("type") != "access":
                return None
            return int(user_id) if user_id else None
        except jwt.PyJWTError:
            return None

    @staticmethod
    def verify_refresh_token(token: str) -> Optional[int]:
        try:
            payload = jwt.decode(token, settings.JWT_REFRESH_SECRET, algorithms=["HS256"])
            user_id = payload.get("sub")
            if payload.get("type") != "refresh":
                return None
            return int(user_id) if user_id else None
        except jwt.PyJWTError:
            return None

    # ==================== Регистрация и логин ====================
    @staticmethod
    def register(db: Session, data: RegisterRequest) -> User:
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise ValueError("Email already registered")
        hashed_password = AuthService.hash_password(data.password)
        user = User(
            email=data.email,
            password_hash=hashed_password,
            full_name=data.full_name,
            phone=None,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def login(db: Session, data: LoginRequest) -> Tuple[User, str, str]:
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            raise ValueError("Invalid credentials")
        if not AuthService.verify_password(data.password, user.password_hash):
            raise ValueError("Invalid credentials")
        access_token = AuthService.create_access_token({"sub": str(user.id)})
        refresh_token = AuthService.create_refresh_token({"sub": str(user.id)})
        AuthService.save_refresh_token(db, user.id, refresh_token)
        return user, access_token, refresh_token

    # ==================== Refresh Token ====================
    @staticmethod
    def save_refresh_token(db: Session, user_id: int, refresh_token: str) -> RefreshToken:
        token_hash = AuthService.hash_token(refresh_token)
        expires_at = datetime.utcnow() + timedelta(minutes=settings.JWT_REFRESH_EXPIRATION)
        refresh_token_db = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            is_revoked=False
        )
        db.add(refresh_token_db)
        db.commit()
        db.refresh(refresh_token_db)
        return refresh_token_db

    @staticmethod
    def find_refresh_token(db: Session, refresh_token: str) -> Optional[RefreshToken]:
        token_hash = AuthService.hash_token(refresh_token)
        return db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        ).first()

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> Optional[str]:
        token_record = AuthService.find_refresh_token(db, refresh_token)
        if not token_record:
            return None
        user_id = AuthService.verify_refresh_token(refresh_token)
        if not user_id:
            return None
        return AuthService.create_access_token({"sub": str(user_id)})

    @staticmethod
    def logout(db: Session, refresh_token: str) -> bool:
        token_hash = AuthService.hash_token(refresh_token)
        token_record = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash
        ).first()
        if token_record:
            token_record.is_revoked = True
            db.commit()
            return True
        return False

    @staticmethod
    def logout_all(db: Session, user_id: int) -> int:
        result = db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        ).update({"is_revoked": True})
        db.commit()
        return result

    # ==================== OAuth Yandex (ПОЛНАЯ ВЕРСИЯ) ====================
    @staticmethod
    async def handle_yandex_oauth(
            db: Session,
            code: str,
            response: Response
    ) -> Dict[str, Any]:
        """Полная обработка OAuth Яндекс"""
        print("=== ПОЛНАЯ ОБРАБОТКА OAuth ===")
        print(f"Получен code: {code}")

        client_id = "2d625c05258d4ca0ac07c74f0d6f6954"
        client_secret = "558ee78782884857aefa1eea025a2ff7"

        # 1. Обмен code на токен
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth.yandex.ru/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            if token_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to exchange code")

            token_data = token_response.json()
            yandex_access_token = token_data.get("access_token")
            print(f"✅ Токен Яндекса получен")

        # 2. Получение данных пользователя
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                "https://login.yandex.ru/info",
                params={"format": "json"},
                headers={"Authorization": f"OAuth {yandex_access_token}"}
            )
            if user_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get user info")

            user_info = user_response.json()
            print(f"✅ Данные пользователя получены")

        # 3. Извлечение данных
        yandex_id = str(user_info.get("id"))
        email = user_info.get("default_email") or user_info.get("emails", [None])[0]
        full_name = user_info.get("real_name") or user_info.get("display_name") or "Yandex User"

        print(f"Yandex ID: {yandex_id}, Email: {email}, Имя: {full_name}")

        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Yandex")

        # 4. Поиск или создание пользователя
        user = db.query(User).filter(User.yandex_id == yandex_id).first()
        if not user:
            user = db.query(User).filter(User.email == email).first()

        if not user:
            print("Создаём нового пользователя...")
            hashed_password = AuthService.hash_password(secrets.token_urlsafe(32))
            user = User(
                email=email,
                password_hash=hashed_password,
                full_name=full_name,
                yandex_id=yandex_id,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ Создан новый пользователь: {user.email} (id={user.id})")
        else:
            if not user.yandex_id:
                user.yandex_id = yandex_id
                db.commit()
                print(f"✅ Обновлён пользователь: {user.email}, добавлен yandex_id")
            else:
                print(f"✅ Пользователь уже существует: {user.email}")

        # 5. Генерация JWT токенов
        access_token_jwt = AuthService.create_access_token({"sub": str(user.id)})
        refresh_token_jwt = AuthService.create_refresh_token({"sub": str(user.id)})

        # 6. Сохранение refresh_token в БД
        AuthService.save_refresh_token(db, user.id, refresh_token_jwt)

        # 7. Установка cookies
        response.set_cookie(
            key="access_token",
            value=access_token_jwt,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=15 * 60
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token_jwt,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=7 * 24 * 60 * 60
        )

        print("✅ OAuth полностью завершён!")

        return {
            "message": "Logged in with Yandex",
            "user": {"id": user.id, "email": user.email, "full_name": user.full_name}
        }