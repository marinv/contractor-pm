from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.worker_type import WorkerType
from app.schemas.worker_type import WorkerTypeCreate, WorkerTypeUpdate, WorkerTypeResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/worker-types", tags=["worker-types"])


@router.get("", response_model=List[WorkerTypeResponse])
def get_worker_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(WorkerType).filter(WorkerType.user_id == current_user.id).all()


@router.post("", response_model=WorkerTypeResponse)
def create_worker_type(
    worker_type_data: WorkerTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    worker_type = WorkerType(
        user_id=current_user.id,
        name=worker_type_data.name,
        hourly_rate=worker_type_data.hourly_rate,
    )
    db.add(worker_type)
    db.commit()
    db.refresh(worker_type)
    return worker_type


@router.put("/{worker_type_id}", response_model=WorkerTypeResponse)
def update_worker_type(
    worker_type_id: int,
    worker_type_data: WorkerTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    worker_type = db.query(WorkerType).filter(
        WorkerType.id == worker_type_id,
        WorkerType.user_id == current_user.id
    ).first()
    if not worker_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker type not found"
        )

    update_data = worker_type_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(worker_type, key, value)

    db.commit()
    db.refresh(worker_type)
    return worker_type


@router.delete("/{worker_type_id}")
def delete_worker_type(
    worker_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    worker_type = db.query(WorkerType).filter(
        WorkerType.id == worker_type_id,
        WorkerType.user_id == current_user.id
    ).first()
    if not worker_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker type not found"
        )

    db.delete(worker_type)
    db.commit()
    return {"message": "Worker type deleted"}
