from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.client import Client
from models.user import User
from schemas.request.customer import CustomerCreate, CustomerUpdate
from schemas.response.customer import CustomerResponse
from utils import get_current_user
from utils.auth import get_db

router = APIRouter(prefix="/client", tags=["Client"])


@router.get("", response_model=List[CustomerResponse])
def get_client(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """Get all clients for the current user's organization"""
    clients = (
        db.query(Client)
        .filter(Client.organization_id == current_user.organization_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return clients


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific customer by ID"""
    customer = (
        db.query(Client)
        .filter(
            Client.id == customer_id,
            Client.organization_id == current_user.organization_id,
        )
        .first()
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("", response_model=CustomerResponse)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new customer"""
    # Check if email is already registered in the organization
    if customer.email:
        existing_customer = (
            db.query(Customer)
            .filter(
                Customer.email == customer.email,
                Customer.organization_id == current_user.organization_id,
            )
            .first()
        )
        if existing_customer:
            raise HTTPException(
                status_code=400,
                detail="A customer with this email already exists in your organization",
            )

    db_customer = Customer(
        **customer.dict(), organization_id=current_user.organization_id
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a customer"""
    db_customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.organization_id == current_user.organization_id,
        )
        .first()
    )
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Check email uniqueness if being updated
    if customer.email and customer.email != db_customer.email:
        existing_customer = (
            db.query(Customer)
            .filter(
                Customer.email == customer.email,
                Customer.organization_id == current_user.organization_id,
            )
            .first()
        )
        if existing_customer:
            raise HTTPException(
                status_code=400,
                detail="A customer with this email already exists in your organization",
            )

    for field, value in customer.dict(exclude_unset=True).items():
        setattr(db_customer, field, value)

    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a customer"""
    db_customer = (
        db.query(Customer)
        .filter(
            Customer.id == customer_id,
            Customer.organization_id == current_user.organization_id,
        )
        .first()
    )
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.delete(db_customer)
    db.commit()
    return {"message": "Customer deleted successfully"}
