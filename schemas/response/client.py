from datetime import datetime
from pydantic import BaseModel, EmailStr


class ClientResponse(BaseModel):
    id: int
    name: str
    email: EmailStr | None
    phone: str | None
    address: str | None
    tax_number: str | None
    is_active: bool
    organization_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
