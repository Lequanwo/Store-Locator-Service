from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import jwt

from app.db.database import get_db
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.auth import LoginRequest, RefreshRequest, LogoutRequest
from app.auth.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_token,
    decode_token,
)

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    access_token = create_access_token(user)
    refresh_token, expires_at = create_refresh_token(user)

    db_refresh = RefreshToken(
        token_hash=hash_token(refresh_token),
        user_id=user.user_id,
        expires_at=expires_at,
        revoked=False,
    )

    db.add(db_refresh)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = decode_token(body.refresh_token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    token_hash = hash_token(body.refresh_token)

    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.revoked == False,
    ).first()

    if not db_token:
        raise HTTPException(status_code=401, detail="Refresh token revoked or not found")

    expires_at = db_token.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = db.query(User).filter(User.user_id == payload["user_id"]).first()

    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="User inactive")

    new_access_token = create_access_token(user)

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(body: LogoutRequest, db: Session = Depends(get_db)):
    token_hash = hash_token(body.refresh_token)

    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
    ).first()

    if db_token:
        db_token.revoked = True
        db.commit()

    return {"message": "Logged out successfully"}