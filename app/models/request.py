from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    request_type = Column(String, nullable=False)
    current_department = Column(String, nullable=False)
    status = Column(String, default="Pending")
    priority = Column(String, default="Normal")  # Low, Normal, High, Urgent
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("Patient")