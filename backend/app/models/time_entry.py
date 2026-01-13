from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from datetime import date

from app.database import Base


class TimeEntry(Base):
    __tablename__ = "time_entries"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    worker_type_id = Column(Integer, ForeignKey("worker_types.id"), nullable=False)
    hours = Column(Float, nullable=False)
    date = Column(Date, default=date.today)
    description = Column(Text, nullable=True)

    project = relationship("Project", back_populates="time_entries")
    worker_type = relationship("WorkerType", back_populates="time_entries")
