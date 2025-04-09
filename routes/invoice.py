from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.invoice import Invoice, InvoiceItem
from models.user import User
from schemas.request import InvoiceCreate, InvoiceUpdate
from schemas.response import InvoiceResponse
from utils import get_current_user
from utils.auth import get_db

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.get("", response_model=List[InvoiceResponse])
def get_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """Get all invoices for the current user's organization"""
    invoices = db.query(Invoice).offset(skip).limit(limit).all()
    return invoices


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific invoice by ID"""
    invoice = (
        db.query(Invoice)
        .filter(
            Invoice.id == invoice_id,
            Invoice.organization_id == current_user.organization_id,
        )
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.post("", response_model=InvoiceResponse)
def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new invoice with items"""
    # Calculate totals
    subtotal = sum(item.quantity * item.unit_price for item in invoice.items)
    tax_amount = subtotal * invoice.tax_rate if invoice.tax_rate else 0
    total = subtotal + tax_amount

    # Create invoice
    db_invoice = Invoice(
        invoice_number=invoice.invoice_number,
        status=invoice.status,
        issue_date=invoice.issue_date,
        due_date=invoice.due_date,
        subtotal=subtotal,
        tax_rate=invoice.tax_rate,
        tax_amount=tax_amount,
        total=total,
        notes=invoice.notes,
        customer_id=invoice.customer_id,
        organization_id=current_user.organization_id,
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)

    # Create invoice items
    for item in invoice.items:
        db_item = InvoiceItem(
            invoice_id=db_invoice.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.quantity * item.unit_price,
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_invoice)
    return db_invoice


@router.patch("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: int,
    invoice: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an invoice"""
    db_invoice = (
        db.query(Invoice)
        .filter(
            Invoice.id == invoice_id,
            Invoice.organization_id == current_user.organization_id,
        )
        .first()
    )
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Update invoice fields
    update_data = invoice.dict(exclude_unset=True)

    # If items are being updated, recalculate totals
    if "items" in update_data:
        # Delete existing items
        db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice_id).delete()

        # Add new items
        subtotal = 0
        for item in invoice.items:
            db_item = InvoiceItem(
                invoice_id=invoice_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.quantity * item.unit_price,
            )
            subtotal += db_item.subtotal
            db.add(db_item)

        # Update invoice totals
        tax_rate = (
            invoice.tax_rate if invoice.tax_rate is not None else db_invoice.tax_rate
        )
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount

        update_data.update(
            {"subtotal": subtotal, "tax_amount": tax_amount, "total": total}
        )

    for field, value in update_data.items():
        if field != "items":  # Skip items as they're handled separately
            setattr(db_invoice, field, value)

    db.commit()
    db.refresh(db_invoice)
    return db_invoice


@router.delete("/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an invoice"""
    db_invoice = (
        db.query(Invoice)
        .filter(
            Invoice.id == invoice_id,
            Invoice.organization_id == current_user.organization_id,
        )
        .first()
    )
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Delete invoice items first (due to foreign key constraint)
    db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice_id).delete()

    # Delete invoice
    db.delete(db_invoice)
    db.commit()
    return {"message": "Invoice deleted successfully"}
