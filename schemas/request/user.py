from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    first_name: str
    middle_name: str | None = None
    last_name: str | None = None
    password: str


class UserLogin(UserBase):
    password: str


class RefreshToken(BaseModel):
    refresh_token: str


class OrganizationBase(BaseModel):
    name: str
    description: str | None = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
