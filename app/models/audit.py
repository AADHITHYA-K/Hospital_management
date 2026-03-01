from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey("requests.id"))
    action = Column(String)
    performed_by = Column(String)
    department = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())