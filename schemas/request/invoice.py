from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
from models.invoice import InvoiceStatus


class InvoiceItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)


class InvoiceBase(BaseModel):
    invoice_number: str = Field(..., min_length=1, max_length=50)
    status: InvoiceStatus = InvoiceStatus.DRAFT
    issue_date: datetime
    due_date: datetime
    tax_rate: float = Field(default=0, ge=0, le=1)
    notes: str | None = Field(None, max_length=1000)
    customer_id: int


class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemBase]


class InvoiceItemUpdate(InvoiceItemBase):
    product_id: int | None = None
    quantity: int | None = Field(None, gt=0)
    unit_price: float | None = Field(None, gt=0)


class InvoiceUpdate(BaseModel):
    invoice_number: str | None = Field(None, min_length=1, max_length=50)
    status: InvoiceStatus | None = None
    issue_date: datetime | None = None
    due_date: datetime | None = None
    tax_rate: float | None = Field(None, ge=0, le=1)
    notes: str | None = Field(None, max_length=1000)
    customer_id: int | None = None
    items: List[InvoiceItemBase] | None = None
