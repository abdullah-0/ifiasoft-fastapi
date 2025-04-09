from datetime import datetime

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config import get_db, SECRET_KEY, ALGORITHM
from models.user import User, Token
from schemas.request import UserLogin, UserCreate, RefreshToken
from schemas.response import UserAuthResponse, TokenResponse, UserResponse
from utils import (
    verify_password,
    get_password_hash,
    get_current_user,
)
from utils.auth import create_tokens

router = APIRouter(prefix="/auth", tags=["Authentication & User"])


@router.post("/register", response_model=UserAuthResponse, status_code=201)
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
    # email_service.send_verification_email(
    #     db_user.email, db_user.email_verification_token
    # )

    # Create tokens
    tokens = create_tokens(db_user.id, db)

    return {
        "user": db_user,
        "token": tokens,
    }


@router.post("/token", response_model=UserAuthResponse)
def login_for_access_token(request_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request_data.email).first()
    if not user or not verify_password(request_data.password, user.password):
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

    tokens = create_tokens(user.id, db)
    return {
        "user": user,
        "token": tokens,
    }

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    token_data: RefreshToken,
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
        tokens = create_tokens(user_id, db)

        return tokens
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


@router.get("/user/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.delete("/user/", responses={}, status_code=204)
def read_user_me(current_user: User = Depends(get_current_user)):
    return
