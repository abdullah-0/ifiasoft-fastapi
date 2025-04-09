import uuid
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    get_db, pwd_context, oauth2_scheme,
)
from models.user import User, Token


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_tokens(user_id: int, db: Session) -> dict[str, str]:
    """
    Create access and refresh tokens for a user.

    Args:
        user_id: The user's ID
        db: Database session

    Returns:
        Tuple of (access_token, refresh_token)
    """
    # Create JWT claims
    access_jti = str(uuid.uuid4())
    refresh_jti = str(uuid.uuid4())

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={"sub": str(user_id), "jti": access_jti},
        expires_delta=access_token_expires,
    )

    # Create refresh token
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_token(
        data={"sub": str(user_id), "jti": refresh_jti},
        expires_delta=refresh_token_expires,
    )

    # Store tokens in database
    db_access_token = Token(
        jti=access_jti,
        token_type="access",
        user_id=user_id,
        expires_at=datetime.utcnow() + access_token_expires,
    )
    db_refresh_token = Token(
        jti=refresh_jti,
        token_type="refresh",
        user_id=user_id,
        expires_at=datetime.utcnow() + refresh_token_expires,
    )

    db.add(db_access_token)
    db.add(db_refresh_token)
    db.commit()

    return {"access": access_token, "refresh": refresh_token}


def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT token.

    Args:
        data: The data to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        The encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Get the current user from the JWT token.

    Args:
        token: The JWT token
        db: Database session

    Returns:
        The current user

    Raises:
        HTTPException: If the token is invalid or the user doesn't exist
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        jti: str = payload.get("jti")
        if user_id is None or jti is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    # Check if token is blacklisted
    token_record = (
        db.query(Token)
        .filter(
            Token.jti == jti,
            Token.revoked == False,
            Token.expires_at > datetime.utcnow(),
        )
        .first()
    )
    if not token_record:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


def revoke_token(token: str, db: Session) -> None:
    """
    Revoke a JWT token.

    Args:
        token: The JWT token to revoke
        db: Database session
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if jti:
            token_record = db.query(Token).filter(Token.jti == jti).first()
            if token_record:
                token_record.revoked = True
                db.commit()
    except jwt.PyJWTError:
        pass
