from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        description="Email пользователя",
        example="user@example.com"
    )
    password: str = Field(
        ...,
        min_length=6,
        description="Пароль (минимум 6 символов)",
        example="password123"
    )

class RegisterRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        description="Email пользователя",
        example="user@example.com"
    )
    password: str = Field(
        ...,
        min_length=6,
        description="Пароль (минимум 6 символов)",
        example="password123"
    )
    full_name: Optional[str] = Field(
        None,
        max_length=255,
        description="Полное имя пользователя",
        example="Иван Петров"
    )

class WhoamiResponse(BaseModel):
    id: int = Field(
        ...,
        description="Уникальный идентификатор пользователя",
        example=1
    )
    email: str = Field(
        ...,
        description="Email пользователя",
        example="user@example.com"
    )
    full_name: Optional[str] = Field(
        None,
        description="Полное имя пользователя",
        example="Иван Петров"
    )