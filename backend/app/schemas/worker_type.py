from pydantic import BaseModel
from typing import Optional


class WorkerTypeCreate(BaseModel):
    name: str
    hourly_rate: float


class WorkerTypeUpdate(BaseModel):
    name: Optional[str] = None
    hourly_rate: Optional[float] = None


class WorkerTypeResponse(BaseModel):
    id: int
    user_id: int
    name: str
    hourly_rate: float

    class Config:
        from_attributes = True
