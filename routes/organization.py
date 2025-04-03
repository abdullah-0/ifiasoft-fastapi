# from typing import List
#
# from fastapi import APIRouter, Depends
# from schemas.request.organization import OrganizationCreate
# from schemas.response.organization import OrganizationResponse
# from sqlalchemy.orm import Session
#
# from config import get_db
# from models.organization import Organization
#
# router = APIRouter(prefix="/organizations", tags=["organizations"])
#
#
# @router.post("/", response_model=OrganizationResponse)
# def create_organization(
#     organization: OrganizationCreate, db: Session = Depends(get_db)
# ):
#     db_org = Organization(**organization.dict())
#     db.add(db_org)
#     db.commit()
#     db.refresh(db_org)
#     return db_org
#
#
# @router.get("/", response_model=List[OrganizationResponse])
# def read_organizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     organizations = db.query(Organization).offset(skip).limit(limit).all()
#     return organizations
