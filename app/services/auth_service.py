import bcrypt
import jwt
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from typing import Optional, Tuple

from app.core.config import settings
from app.models.user import User
from app.models.token import RefreshToken
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthService:

    @staticmethod
    def hash_password(password: str) -> Tuple[str, str]:
        """Хеширование пароля с солью"""
        salt = bcrypt.gensalt().decode('utf-8')
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8')).decode('utf-8')
        return hashed, salt

    @staticmethod
    def verify_password(password: str, hashed: str, salt: str) -> bool:
        """Проверка пароля"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    @staticmethod
    def generate_access_token(user_id: int) -> str:
        """Генерация Access Token"""
        payload = {
            "sub": str(user_id),
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15)
        }
        return jwt.encode(payload, settings.JWT_ACCESS_SECRET, algorithm="HS256")

    @staticmethod
    def generate_refresh_token() -> str:
        """Генерация Refresh Token (случайная строка)"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def verify_access_token(token: str) -> Optional[int]:
        """Проверка Access Token"""
        try:
            payload = jwt.decode(token, settings.JWT_ACCESS_SECRET, algorithms=["HS256"])
            return int(payload.get("sub"))
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def register(db: Session, data: RegisterRequest) -> User:
        """Регистрация пользователя"""
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise ValueError("Email already registered")

        hashed, salt = AuthService.hash_password(data.password)
        user = User(
            email=data.email,
            password_hash=hashed,
            salt=salt,
            full_name=data.full_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def login(db: Session, data: LoginRequest) -> Tuple[User, str, str]:
        """Вход пользователя"""
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            raise ValueError("Invalid credentials")

        if not AuthService.verify_password(data.password, user.password_hash, user.salt):
            raise ValueError("Invalid credentials")

        access_token = AuthService.generate_access_token(user.id)
        refresh_token = AuthService.generate_refresh_token()

        # Сохраняем refresh token в БД
        hashed_refresh = bcrypt.hashpw(refresh_token.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        db_refresh = RefreshToken(
            user_id=user.id,
            token_hash=hashed_refresh,
            expires_at=expires_at
        )
        db.add(db_refresh)
        db.commit()

        return user, access_token, refresh_token

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> Optional[str]:
        """Обновление Access Token по Refresh Token"""
        tokens = db.query(RefreshToken).filter(
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.now(timezone.utc)
        ).all()

        for token in tokens:
            if bcrypt.checkpw(refresh_token.encode('utf-8'), token.token_hash.encode('utf-8')):
                return AuthService.generate_access_token(token.user_id)

        return None

    @staticmethod
    def logout(db: Session, refresh_token: str) -> bool:
        """Завершение текущей сессии"""
        tokens = db.query(RefreshToken).filter(RefreshToken.is_revoked == False).all()
        for token in tokens:
            if bcrypt.checkpw(refresh_token.encode('utf-8'), token.token_hash.encode('utf-8')):
                token.is_revoked = True
                db.commit()
                return True
        return False

    @staticmethod
    def logout_all(db: Session, user_id: int) -> int:
        """Завершение всех сессий пользователя"""
        count = db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        ).update({"is_revoked": True})
        db.commit()
        return count