from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from app.database import Base
import datetime


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey("requests.id"))
    department = Column(String, nullable=False)
    status = Column(String, default="Pending")  # Pending, In Progress, Completed, Escalated

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    duration_seconds = Column(Integer, nullable=True)
    sla_breached = Column(Boolean, default=False)
    due_at = Column(DateTime, nullable=True)  # For SLA monitoring
