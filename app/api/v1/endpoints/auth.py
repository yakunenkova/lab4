from fastapi import APIRouter, Depends, HTTPException, Response, Request, Cookie
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest, RegisterRequest, WhoamiResponse
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = AuthService.register(db, data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
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


@router.post("/refresh")
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


@router.get("/whoami", response_model=WhoamiResponse)
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


@router.post("/logout")
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


@router.post("/logout-all")
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