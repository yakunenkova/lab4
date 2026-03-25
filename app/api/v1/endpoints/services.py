from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import math

from app.core.database import get_db
from app.services.service_service import ServiceService
from app.schemas.service import ServiceResponse, ServiceCreate, ServiceUpdate
from app.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/services", tags=["services"])


@router.get("/", response_model=PaginatedResponse[ServiceResponse])
def get_services(
        page: int = Query(1, ge=1),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    services, total = ServiceService.get_services(db, page, limit)
    total_pages = math.ceil(total / limit) if total > 0 else 1

    return PaginatedResponse(
        data=services,
        meta={
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        }
    )


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = ServiceService.get_service(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post("/", response_model=ServiceResponse, status_code=201)
def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    return ServiceService.create_service(db, service)


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(service_id: int, service: ServiceCreate, db: Session = Depends(get_db)):
    updated = ServiceService.update_service(db, service_id, ServiceUpdate(**service.dict()))
    if not updated:
        raise HTTPException(status_code=404, detail="Service not found")
    return updated


@router.patch("/{service_id}", response_model=ServiceResponse)
def patch_service(service_id: int, service: ServiceUpdate, db: Session = Depends(get_db)):
    updated = ServiceService.update_service(db, service_id, service)
    if not updated:
        raise HTTPException(status_code=404, detail="Service not found")
    return updated


@router.delete("/{service_id}", status_code=204)
def delete_service(service_id: int, db: Session = Depends(get_db)):
    deleted = ServiceService.soft_delete_service(db, service_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Service not found")
    return None