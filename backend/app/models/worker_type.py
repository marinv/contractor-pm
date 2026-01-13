from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class WorkerType(Base):
    __tablename__ = "worker_types"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    hourly_rate = Column(Float, nullable=False)

    owner = relationship("User", back_populates="worker_types")
    time_entries = relationship("TimeEntry", back_populates="worker_type")
