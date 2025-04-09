import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from config import Base
from .enums import InvoiceStatus


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, index=True)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    issue_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    subtotal = Column(Float, nullable=False)
    tax_rate = Column(Float, default=0)
    tax_amount = Column(Float, default=0)
    total = Column(Float, nullable=False)
    notes = Column(String(1000))

    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="invoices")

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="invoices")

    # Define the items relationship explicitly
    items = relationship("InvoiceItem", back_populates="invoice")

    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    updated_at = Column(
        DateTime,
        default=datetime.datetime.now(datetime.UTC),
        onupdate=datetime.datetime.now(datetime.UTC),
    )


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    invoice = relationship("Invoice", back_populates="items")

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product = relationship("Product", back_populates="invoice_items")

    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    updated_at = Column(
        DateTime,
        default=datetime.datetime.now(datetime.UTC),
        onupdate=datetime.datetime.now(datetime.UTC),
    )
