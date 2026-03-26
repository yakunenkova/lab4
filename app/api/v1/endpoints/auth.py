from fastapi import APIRouter, Depends, HTTPException, Response, Request, Cookie, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest, RegisterRequest, WhoamiResponse
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создает нового пользователя с хешированием пароля. Пароль не возвращается в ответе.",
    responses={
        201: {"description": "Пользователь успешно создан"},
        400: {"description": "Email уже зарегистрирован или неверные данные"}
    }
)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = AuthService.register(db, data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Вход в систему",
    description="Аутентифицирует пользователя и устанавливает HttpOnly cookies с access_token и refresh_token.",
    responses={
        200: {"description": "Успешный вход, cookies установлены"},
        401: {"description": "Неверный email или пароль"}
    }
)
def login(
        response: Response,
        data: LoginRequest,
        db: Session = Depends(get_db)
):
    try:
        user, access_token, refresh_token = AuthService.login(db, data)

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=15 * 60
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=7 * 24 * 60 * 60
        )

        return {"message": "Logged in successfully"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    summary="Обновление токенов",
    description="Использует refresh_token из cookies для выдачи нового access_token.",
    responses={
        200: {"description": "Токен обновлен, новый access_token установлен в cookie"},
        401: {"description": "Refresh token отсутствует, истек или недействителен"}
    }
)
def refresh(
        response: Response,
        refresh_token: Optional[str] = Cookie(None),
        db: Session = Depends(get_db)
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    new_access = AuthService.refresh_access_token(db, refresh_token)
    if not new_access:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    response.set_cookie(
        key="access_token",
        value=new_access,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=15 * 60
    )

    return {"message": "Token refreshed"}


@router.get(
    "/whoami",
    response_model=WhoamiResponse,
    summary="Проверка авторизации",
    description="Возвращает данные текущего авторизованного пользователя. Требует access_token в cookies.",
    responses={
        200: {"description": "Пользователь авторизован, возвращены данные"},
        401: {"description": "Не авторизован, токен отсутствует или недействителен"}
    }
)
def whoami(
        request: Request,
        access_token: Optional[str] = Cookie(None),
        db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = AuthService.verify_access_token(access_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    from app.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return WhoamiResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Выход из системы",
    description="Завершает текущую сессию, отзывая refresh_token и удаляя cookies.",
    responses={
        200: {"description": "Успешный выход, cookies удалены"},
        401: {"description": "Не авторизован"}
    }
)
def logout(
        response: Response,
        refresh_token: Optional[str] = Cookie(None),
        db: Session = Depends(get_db)
):
    if refresh_token:
        AuthService.logout(db, refresh_token)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"message": "Logged out"}


@router.post(
    "/logout-all",
    status_code=status.HTTP_200_OK,
    summary="Выход из всех устройств",
    description="Отзывает все refresh токены пользователя, завершая все активные сессии.",
    responses={
        200: {"description": "Все сессии завершены"},
        401: {"description": "Не авторизован"}
    }
)
def logout_all(
        response: Response,
        access_token: Optional[str] = Cookie(None),
        db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = AuthService.verify_access_token(access_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    AuthService.logout_all(db, user_id)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"message": "All sessions terminated"}