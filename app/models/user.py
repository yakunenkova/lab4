from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # хеш пароля
    salt = Column(String(255), nullable=False)  # уникальная соль
    full_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    yandex_id = Column(String(255), nullable=True, unique=True)  # для OAuth
    vk_id = Column(String(255), nullable=True, unique=True)  # для OAuth
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # soft delete