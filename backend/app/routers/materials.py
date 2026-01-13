from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.material import Material
from app.schemas.material import MaterialCreate, MaterialUpdate, MaterialResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/api", tags=["materials"])


def verify_project_ownership(project_id: int, user_id: int, db: Session):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id
    ).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project


@router.get("/projects/{project_id}/materials", response_model=List[MaterialResponse])
def get_materials(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_project_ownership(project_id, current_user.id, db)
    return db.query(Material).filter(Material.project_id == project_id).all()


@router.post("/projects/{project_id}/materials", response_model=MaterialResponse)
def create_material(
    project_id: int,
    material_data: MaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_project_ownership(project_id, current_user.id, db)

    material = Material(
        project_id=project_id,
        name=material_data.name,
        quantity=material_data.quantity,
        unit=material_data.unit,
        unit_price=material_data.unit_price,
        supplier=material_data.supplier,
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


@router.put("/materials/{material_id}", response_model=MaterialResponse)
def update_material(
    material_id: int,
    material_data: MaterialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    material = db.query(Material).join(Project).filter(
        Material.id == material_id,
        Project.user_id == current_user.id
    ).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )

    update_data = material_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(material, key, value)

    db.commit()
    db.refresh(material)
    return material


@router.delete("/materials/{material_id}")
def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    material = db.query(Material).join(Project).filter(
        Material.id == material_id,
        Project.user_id == current_user.id
    ).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )

    db.delete(material)
    db.commit()
    return {"message": "Material deleted"}
