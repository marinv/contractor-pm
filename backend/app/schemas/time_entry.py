from pydantic import BaseModel
from datetime import date as date_type
from typing import Union


class TimeEntryCreate(BaseModel):
    worker_type_id: int
    hours: float
    date: Union[date_type, None] = None
    description: Union[str, None] = None


class TimeEntryUpdate(BaseModel):
    worker_type_id: Union[int, None] = None
    hours: Union[float, None] = None
    date: Union[date_type, None] = None
    description: Union[str, None] = None


class TimeEntryResponse(BaseModel):
    id: int
    project_id: int
    worker_type_id: int
    hours: float
    date: date_type
    description: Union[str, None] = None

    class Config:
        from_attributes = True
