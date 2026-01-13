from typing import List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.time_entry import TimeEntry
from app.models.worker_type import WorkerType
from app.schemas.time_entry import TimeEntryCreate, TimeEntryUpdate, TimeEntryResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/api", tags=["time-entries"])


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


@router.get("/projects/{project_id}/time-entries", response_model=List[TimeEntryResponse])
def get_time_entries(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verify_project_ownership(project_id, current_user.id, db)
    return db.query(TimeEntry).filter(TimeEntry.project_id == project_id).all()


@router.post("/projects/{project_id}/time-entries-debug")
async def debug_time_entry(project_id: int, request: Request):
    body = await request.json()
    print(f"DEBUG - Raw request body: {body}")
    return {"received": body}


@router.post("/projects/{project_id}/time-entries", response_model=TimeEntryResponse)
def create_time_entry(
    project_id: int,
    entry_data: TimeEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print(f"Received time entry data: {entry_data}")
    verify_project_ownership(project_id, current_user.id, db)

    # Verify worker type belongs to user
    worker_type = db.query(WorkerType).filter(
        WorkerType.id == entry_data.worker_type_id,
        WorkerType.user_id == current_user.id
    ).first()
    if not worker_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid worker type"
        )

    time_entry = TimeEntry(
        project_id=project_id,
        worker_type_id=entry_data.worker_type_id,
        hours=entry_data.hours,
        date=entry_data.date or date.today(),
        description=entry_data.description,
    )
    db.add(time_entry)
    db.commit()
    db.refresh(time_entry)
    return time_entry


@router.put("/time-entries/{entry_id}", response_model=TimeEntryResponse)
def update_time_entry(
    entry_id: int,
    entry_data: TimeEntryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    time_entry = db.query(TimeEntry).join(Project).filter(
        TimeEntry.id == entry_id,
        Project.user_id == current_user.id
    ).first()
    if not time_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found"
        )

    update_data = entry_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(time_entry, key, value)

    db.commit()
    db.refresh(time_entry)
    return time_entry


@router.delete("/time-entries/{entry_id}")
def delete_time_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    time_entry = db.query(TimeEntry).join(Project).filter(
        TimeEntry.id == entry_id,
        Project.user_id == current_user.id
    ).first()
    if not time_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time entry not found"
        )

    db.delete(time_entry)
    db.commit()
    return {"message": "Time entry deleted"}
