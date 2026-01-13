from pydantic import BaseModel
from typing import Optional


class MaterialCreate(BaseModel):
    name: str
    quantity: float
    unit: str
    unit_price: float
    supplier: Optional[str] = None


class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    supplier: Optional[str] = None


class MaterialResponse(BaseModel):
    id: int
    project_id: int
    name: str
    quantity: float
    unit: str
    unit_price: float
    supplier: Optional[str]

    class Config:
        from_attributes = True
