from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ServiceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    duration: int = Field(..., ge=5, le=480)
    price: float = Field(..., ge=0)
    category: str = Field(..., min_length=1, max_length=100)
    status: str = Field("active", pattern="^(active|inactive)$")

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    duration: Optional[int] = Field(None, ge=5, le=480)
    price: Optional[float] = Field(None, ge=0)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")

class ServiceResponse(ServiceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None  # ← сделаем необязательным

    class Config:
        from_attributes = True