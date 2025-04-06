from datetime import datetime
from typing import List
from pydantic import BaseModel
from models.enums import InvoiceStatus


class InvoiceItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    subtotal: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    status: InvoiceStatus
    issue_date: datetime
    due_date: datetime
    subtotal: float
    tax_rate: float
    tax_amount: float
    total: float
    notes: str | None
    customer_id: int
    organization_id: int
    created_at: datetime
    updated_at: datetime
    items: List[InvoiceItemResponse]

    class Config:
        from_attributes = True
