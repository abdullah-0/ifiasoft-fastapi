from datetime import datetime

from pydantic import BaseModel, computed_field


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    middle_name: str
    last_name: str
    is_active: bool
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


class TokenResponse(BaseModel):
    access: str
    refresh: str


class UserAuthResponse(BaseModel):
    user: UserResponse
    token: TokenResponse
