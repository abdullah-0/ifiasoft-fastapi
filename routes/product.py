from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models.product import Product
from models.user import User
from schemas.request import ProductCreate, ProductUpdate
from schemas.response import ProductResponse
from utils import get_current_user
from utils.auth import get_db

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=List[ProductResponse])
def get_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """Get all products for the current user's organization"""
    products = (
        db.query(Product)
        .filter(Product.organization_id == current_user.organization_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific product by ID"""
    product = (
        db.query(Product)
        .filter(
            Product.id == product_id,
            Product.organization_id == current_user.organization_id,
        )
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new product"""
    db_product = Product(**product.dict(), organization_id=current_user.organization_id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a product"""
    db_product = (
        db.query(Product)
        .filter(
            Product.id == product_id,
            Product.organization_id == current_user.organization_id,
        )
        .first()
    )
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in product.dict(exclude_unset=True).items():
        setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a product"""
    db_product = (
        db.query(Product)
        .filter(
            Product.id == product_id,
            Product.organization_id == current_user.organization_id,
        )
        .first()
    )
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}
