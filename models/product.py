import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    sku = Column(String(50), unique=True, index=True)
    unit_price = Column(Float, nullable=False)
    quantity_in_stock = Column(Integer, default=0)
    reorder_level = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="products")

    # Add relationship to invoice items
    invoice_items = relationship("InvoiceItem", back_populates="product")

    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    updated_at = Column(
        DateTime,
        default=datetime.datetime.now(datetime.UTC),
        onupdate=datetime.datetime.now(datetime.UTC),
    )
