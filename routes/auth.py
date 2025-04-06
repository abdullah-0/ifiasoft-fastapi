from datetime import datetime
from typing import Dict, Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from config import get_db, SECRET_KEY, ALGORITHM
from models.user import User
from schemas.request.user import Token, UserCreate, TokenRefresh
from schemas.response.user import UserResponse
from utils import (
    verify_password,
    get_password_hash,
    get_current_user,
)
from utils.auth import create_tokens
from utils.email import email_service

router = APIRouter(prefix="/auth", tags=["Authentication & User"])


@router.post("/register", response_model=Dict[str, Any])
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        password=hashed_password,
        first_name=user.first_name,
        middle_name=user.middle_name,
        last_name=user.last_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Send verification email
    email_service.send_verification_email(
        db_user.email, db_user.email_verification_token
    )

    # Create tokens
    access_token, refresh_token = create_tokens(db_user.id, db)

    return {
        "user": db_user,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )

    access_token, refresh_token = create_tokens(user.id, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(
            token_data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        user_id = payload.get("sub")
        jti = payload.get("jti")

        if not user_id or not jti:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # Verify refresh token in database
        token_record = (
            db.query(Token)
            .filter(
                Token.jti == jti,
                Token.token_type == "refresh",
                Token.revoked == False,
                Token.expires_at > datetime.utcnow(),
            )
            .first()
        )

        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # Revoke the old refresh token
        token_record.revoked = True
        db.commit()

        # Create new tokens
        access_token, refresh_token = create_tokens(user_id, db)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Revoke all user's active tokens
    db.query(Token).filter(
        Token.user_id == current_user.id,
        Token.revoked == False,
        Token.expires_at > datetime.utcnow(),
    ).update({"revoked": True})
    db.commit()

    return {"message": "Successfully logged out"}


@router.get("/verify-email/{token}")
def verify_email(
    token: str,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email_verification_token == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )

    user.is_email_verified = True
    user.email_verification_token = None
    db.commit()

    return {"message": "Email verified successfully"}


@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user
