from pydantic import BaseModel, Field, EmailStr


class ClientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    address: str | None = Field(None, max_length=500)
    tax_number: str | None = Field(None, max_length=50)


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    address: str | None = Field(None, max_length=500)
    tax_number: str | None = Field(None, max_length=50)
    is_active: bool | None = None
