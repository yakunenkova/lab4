from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ServiceBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Название услуги",
        example="Массаж спины"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Описание услуги",
        example="Расслабляющий массаж спины с элементами ароматерапии"
    )
    duration: int = Field(
        ...,
        ge=5,
        le=480,
        description="Длительность услуги в минутах",
        example=60
    )
    price: float = Field(
        ...,
        ge=0,
        description="Цена услуги в рублях",
        example=2500.00
    )
    category: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Категория услуги",
        example="Массаж"
    )
    status: str = Field(
        "active",
        pattern="^(active|inactive)$",
        description="Статус услуги (active - активна, inactive - неактивна)",
        example="active"
    )

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Название услуги",
        example="Массаж спины"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Описание услуги",
        example="Расслабляющий массаж спины"
    )
    duration: Optional[int] = Field(
        None,
        ge=5,
        le=480,
        description="Длительность услуги в минутах",
        example=60
    )
    price: Optional[float] = Field(
        None,
        ge=0,
        description="Цена услуги в рублях",
        example=2500.00
    )
    category: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Категория услуги",
        example="Массаж"
    )
    status: Optional[str] = Field(
        None,
        pattern="^(active|inactive)$",
        description="Статус услуги",
        example="active"
    )

class ServiceResponse(ServiceBase):
    id: int = Field(
        ...,
        description="Уникальный идентификатор услуги",
        example=1
    )
    created_at: datetime = Field(
        ...,
        description="Дата создания",
        example="2026-03-26T20:50:50.916563Z"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Дата последнего обновления",
        example="2026-03-26T21:00:00.000000Z"
    )

    class Config:
        from_attributes = True