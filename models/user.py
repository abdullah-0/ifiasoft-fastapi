import datetime
import uuid

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from config import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(127), nullable=False)
    description = Column(String(255))
    address = Column(String(255))
    phone = Column(String(20))
    email = Column(String(127), unique=True)
    website = Column(String(127))
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    updated_at = Column(
        DateTime,
        default=datetime.datetime.now(datetime.UTC),
        onupdate=datetime.datetime.now(datetime.UTC),
    )

    # Relationships
    users = relationship("User", back_populates="organization")
    invoices = relationship("Invoice", back_populates="organization")
    products = relationship("Product", back_populates="organization")
    clients = relationship("Client", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String(127), unique=True, index=True)
    password = Column(String())
    salutation = Column(String(15))
    first_name = Column(String(63), nullable=False)
    middle_name = Column(String(63), default="")
    last_name = Column(String(63), default="")
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    is_email_verified = Column(Boolean, default=False)
    email_verification_token = Column(
        String(36), unique=True, default=lambda: str(uuid.uuid4())
    )

    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    updated_at = Column(
        DateTime,
        default=datetime.datetime.now(datetime.UTC),
        onupdate=datetime.datetime.now(datetime.UTC),
    )

    role_id = Column(Integer, ForeignKey("roles.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    # Relationships
    role = relationship("Role", back_populates="users")
    organization = relationship("Organization", back_populates="users")
    tokens = relationship("Token", back_populates="user")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    permissions = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    updated_at = Column(
        DateTime,
        default=datetime.datetime.now(datetime.UTC),
        onupdate=datetime.datetime.now(datetime.UTC),
    )

    users = relationship("User", back_populates="role")


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(36), unique=True, index=True)
    token_type = Column(String(10))
    user_id = Column(Integer, ForeignKey("users.id"))
    revoked = Column(Boolean, default=False)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))

    # Relationship
    user = relationship("User", back_populates="tokens")
