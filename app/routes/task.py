from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.task import Task
from app.core.dependencies import get_current_user, get_db
from app.services.workflow_engine import get_user_department
from datetime import datetime

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/my-tasks")
def my_tasks(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_dept = get_user_department(current_user.role)
    if not user_dept:
        return []
    tasks = db.query(Task).filter(
        Task.department == user_dept,
        Task.status != "Completed",
    ).all()

    return [
        {
            "id": t.id,
            "request_id": t.request_id,
            "department": t.department,
            "status": t.status,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "due_at": t.due_at.isoformat() if t.due_at else None,
        }
        for t in tasks
    ]


@router.get("/sla-breaches")
def sla_breaches(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Tasks that have breached SLA (sla_breached=True) or are overdue (not completed, due_at < now)."""
    now = datetime.utcnow()

    overdue = db.query(Task).filter(
        Task.status != "Completed",
        Task.due_at.isnot(None),
        Task.due_at < now,
    ).all()

    already_breached = db.query(Task).filter(Task.sla_breached == True).all()

    seen = set()
    result = []
    for t in overdue:
        if t.id not in seen:
            seen.add(t.id)
            result.append({
                "id": t.id,
                "request_id": t.request_id,
                "department": t.department,
                "status": t.status,
                "due_at": t.due_at.isoformat() if t.due_at else None,
                "overdue": True,
            })
    for t in already_breached:
        if t.id not in seen:
            seen.add(t.id)
            result.append({
                "id": t.id,
                "request_id": t.request_id,
                "department": t.department,
                "status": t.status,
                "sla_breached": True,
            })

    return result
