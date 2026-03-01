from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.core.dependencies import get_db, get_current_user, require_role
from app.models.task import Task

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/department-performance")
def department_performance(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("Admin")),
):
    results = db.query(
        Task.department,
        func.count(Task.id).label("total_tasks"),
        func.sum(case((Task.status == "Completed", 1), else_=0)).label("completed_tasks"),
        func.avg(Task.duration_seconds).label("avg_completion_time"),
        func.sum(case((Task.sla_breached == True, 1), else_=0)).label("sla_breaches"),
    ).group_by(Task.department).all()

    analytics_data = []

    for row in results:
        analytics_data.append({
            "department": row.department,
            "total_tasks": row.total_tasks,
            "completed_tasks": row.completed_tasks or 0,
            "avg_completion_time_seconds": int(row.avg_completion_time or 0),
            "sla_breaches": row.sla_breaches or 0
        })

    return analytics_data   