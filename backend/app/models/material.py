from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text

from sqlalchemy.orm import relationship

from app.database import Base


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)  # e.g., "pcs", "m", "kg", "l"
    unit_price = Column(Float, nullable=False)
    supplier = Column(String, nullable=True)

    project = relationship("Project", back_populates="materials")
