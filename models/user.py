import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime

from config import Base


# from sqlalchemy.orm import relationship


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

    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    updated_at = Column(
        DateTime,
        default=datetime.datetime.now(datetime.UTC),
        onupdate=datetime.datetime.now(datetime.UTC),
    )
    #
    # organization_id = Column(Integer, ForeignKey("organizations.id"))
    # organization = relationship("Organization", back_populates="users")
    #
    # role_id = Column(Integer, ForeignKey("roles.id"))
    # role = relationship("Role", back_populates="users")
