from datetime import datetime

from pydantic import BaseModel


class OrganizationBase(BaseModel):
    name: str
    description: str | None = None


class OrganizationResponse(OrganizationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
