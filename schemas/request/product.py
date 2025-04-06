from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    sku: str = Field(..., min_length=1, max_length=50)
    unit_price: float = Field(..., gt=0)
    quantity_in_stock: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=0, ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    sku: str | None = Field(None, min_length=1, max_length=50)
    unit_price: float | None = Field(None, gt=0)
    quantity_in_stock: int | None = Field(None, ge=0)
    reorder_level: int | None = Field(None, ge=0)
    is_active: bool | None = None
