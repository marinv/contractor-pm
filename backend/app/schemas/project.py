from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.schemas.time_entry import TimeEntryResponse
from app.schemas.material import MaterialResponse


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_address: Optional[str] = None
    status: Optional[str] = "draft"
    offer_terms: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_address: Optional[str] = None
    status: Optional[str] = None
    offer_terms: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    customer_name: Optional[str]
    customer_email: Optional[str]
    customer_address: Optional[str]
    status: str
    offer_terms: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    time_entries: List[TimeEntryResponse] = []
    materials: List[MaterialResponse] = []
