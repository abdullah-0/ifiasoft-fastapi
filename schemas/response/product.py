from datetime import datetime
from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    sku: str
    unit_price: float
    quantity_in_stock: int
    reorder_level: int
    is_active: bool
    organization_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
