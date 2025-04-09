from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.client import Client
from models.user import User
from schemas.request import ClientCreate, ClientUpdate
from schemas.response import ClientResponse
from utils import get_current_user
from utils.auth import get_db

router = APIRouter(prefix="/client", tags=["Client"])


@router.get("", response_model=List[ClientResponse])
def get_clients(
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


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific client by ID"""
    client = (
        db.query(Client)
        .filter(
            Client.id == client_id,
            Client.organization_id == current_user.organization_id,
        )
        .first()
    )
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.post("", response_model=ClientResponse)
def create_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new client"""
    # Check if email is already registered in the organization
    if client.email:
        existing_client = (
            db.query(Client)
            .filter(
                Client.email == client.email,
                Client.organization_id == current_user.organization_id,
            )
            .first()
        )
        if existing_client:
            raise HTTPException(
                status_code=400,
                detail="A client with this email already exists in your organization",
            )

    db_client = Client(**client.dict(), organization_id=current_user.organization_id)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@router.patch("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int,
    client: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a client"""
    db_client = (
        db.query(Client)
        .filter(
            Client.id == client_id,
            Client.organization_id == current_user.organization_id,
        )
        .first()
    )
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Check email uniqueness if being updated
    if client.email and client.email != db_client.email:
        existing_client = (
            db.query(Client)
            .filter(
                Client.email == client.email,
                Client.organization_id == current_user.organization_id,
            )
            .first()
        )
        if existing_client:
            raise HTTPException(
                status_code=400,
                detail="A client with this email already exists in your organization",
            )

    for field, value in client.dict(exclude_unset=True).items():
        setattr(db_client, field, value)

    db.commit()
    db.refresh(db_client)
    return db_client


@router.delete("/{client_id}")
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a client"""
    db_client = (
        db.query(Client)
        .filter(
            Client.id == client_id,
            Client.organization_id == current_user.organization_id,
        )
        .first()
    )
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")

    db.delete(db_client)
    db.commit()
    return {"message": "Client deleted successfully"}
