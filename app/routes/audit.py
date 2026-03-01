from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.audit import AuditLog

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/request/{request_id}")
def get_request_audit_log(
    request_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get full audit trail for a request."""
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.request_id == request_id)
        .order_by(AuditLog.timestamp.asc())
        .all()
    )
    return [
        {
            "id": log.id,
            "request_id": log.request_id,
            "action": log.action,
            "performed_by": log.performed_by,
            "department": log.department,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
        }
        for log in logs
    ]
