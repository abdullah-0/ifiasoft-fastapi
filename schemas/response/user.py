from pydantic import BaseModel, computed_field
from datetime import datetime


class UserBase(BaseModel):
    id: int
    email: str
    first_name: str
    middle_name: str
    last_name: str
    is_active: bool


class UserResponse(UserBase):
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def full_name(self) -> str:
        name_parts = [self.first_name]
        if self.middle_name:
            name_parts.append(self.middle_name)
        name_parts.append(self.last_name)
        return " ".join(name_parts).strip()

    class Config:
        from_attributes = True
