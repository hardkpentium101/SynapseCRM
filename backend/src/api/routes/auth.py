from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.db.database import get_db
from src.db.models import User
from src.db.schemas import LoginRequest
from src.api.deps import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "territory": user.territory,
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role,
        "territory": current_user.territory,
        "created_at": current_user.created_at.isoformat()
        if current_user.created_at
        else None,
        "updated_at": current_user.updated_at.isoformat()
        if current_user.updated_at
        else None,
    }


