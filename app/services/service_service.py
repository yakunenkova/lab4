from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List, Tuple

from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate


class ServiceService:

    @staticmethod
    def create_service(db: Session, service_data: ServiceCreate) -> Service:
        db_service = Service(
            name=service_data.name,
            description=service_data.description,
            duration=service_data.duration,
            price=service_data.price,
            category=service_data.category,
            status=service_data.status
        )
        db.add(db_service)
        db.commit()
        db.refresh(db_service)
        return db_service

    @staticmethod
    def get_service(db: Session, service_id: int) -> Optional[Service]:
        return db.query(Service).filter(
            Service.id == service_id,
            Service.deleted_at.is_(None)
        ).first()

    @staticmethod
    def get_services(db: Session, page: int = 1, limit: int = 10) -> Tuple[List[Service], int]:
        query = db.query(Service).filter(Service.deleted_at.is_(None))
        total = query.count()
        services = query.offset((page - 1) * limit).limit(limit).all()
        return services, total

    @staticmethod
    def update_service(db: Session, service_id: int, service_data: ServiceUpdate) -> Optional[Service]:
        db_service = db.query(Service).filter(
            Service.id == service_id,
            Service.deleted_at.is_(None)
        ).first()
        if not db_service:
            return None

        update_data = service_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_service, field, value)

        db.commit()
        db.refresh(db_service)
        return db_service

    @staticmethod
    def soft_delete_service(db: Session, service_id: int) -> bool:
        db_service = db.query(Service).filter(
            Service.id == service_id,
            Service.deleted_at.is_(None)
        ).first()
        if not db_service:
            return False

        db_service.deleted_at = datetime.utcnow()
        db.commit()
        return True