from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.request import Request
from app.models.task import Task
from app.models.audit import AuditLog
from app.models.patient import Patient
from app.schemas.request import RequestCreate, RequestResponse
from app.services.workflow_engine import get_next_department, WORKFLOWS, can_user_complete_department
import datetime

router = APIRouter(prefix="/requests", tags=["Requests"])


@router.get("/{request_id}/status")
def request_status(
    request_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    tasks = db.query(Task).filter(Task.request_id == request_id).all()
    completed_steps = len([t for t in tasks if t.status == "Completed"])
    total_steps = len(tasks)

    return {
        "request_id": req.id,
        "current_department": req.current_department,
        "status": req.status,
        "steps_completed": completed_steps,
        "total_steps": total_steps,
    }


@router.post("/", response_model=RequestResponse)
def create_request(
    body: RequestCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if body.request_type not in WORKFLOWS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request_type. Allowed: {', '.join(WORKFLOWS.keys())}",
        )
    patient = db.query(Patient).filter(Patient.id == body.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    new_request = Request(
        patient_id=body.patient_id,
        request_type=body.request_type,
        current_department="OPD",
        priority=body.priority or "Normal",
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    # Create first task
    first_task = Task(
        request_id=new_request.id,
        department="OPD",
    )
    from app.services.workflow_engine import SLA_LIMITS
    if "OPD" in SLA_LIMITS:
        from datetime import timedelta
        first_task.due_at = datetime.datetime.utcnow() + timedelta(seconds=SLA_LIMITS["OPD"])

    db.add(first_task)
    db.commit()

    return new_request


@router.get("/", response_model=list[RequestResponse])
def list_requests(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    status: str | None = None,
    request_type: str | None = None,
):
    q = db.query(Request)
    if status:
        q = q.filter(Request.status == status)
    if request_type:
        q = q.filter(Request.request_type == request_type)
    return q.order_by(Request.created_at.desc()).all()


@router.get("/{request_id}", response_model=RequestResponse)
def get_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req


@router.get("/{request_id}/tasks")
def get_request_tasks(
    request_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all tasks (history) for a request."""
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    tasks = db.query(Task).filter(Task.request_id == request_id).order_by(Task.created_at).all()
    return [
        {
            "id": t.id,
            "department": t.department,
            "status": t.status,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            "duration_seconds": t.duration_seconds,
            "sla_breached": t.sla_breached,
        }
        for t in tasks
    ]


@router.post("/{request_id}/complete")
def complete_task(
    request_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    req = db.query(Request).filter(Request.id == request_id).first()

    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    if not can_user_complete_department(current_user.role, req.current_department):
        raise HTTPException(
            status_code=403,
            detail=f"Only {req.current_department} department can complete this task",
        )

    # Get current task
    current_task = db.query(Task).filter(
        Task.request_id == req.id,
        Task.department == req.current_department,
        Task.status.in_(["Pending", "In Progress"]),
    ).first()

    if current_task:
        current_task.status = "Completed"
        current_task.completed_at = datetime.datetime.utcnow()

        duration = (current_task.completed_at - current_task.created_at).total_seconds()
        current_task.duration_seconds = int(duration)

        from app.services.workflow_engine import SLA_LIMITS
        sla_limit = SLA_LIMITS.get(current_task.department)

        if sla_limit and duration > sla_limit:
            current_task.sla_breached = True

        db.commit()

    next_department = get_next_department(req.request_type, req.current_department)

    if next_department:
        req.current_department = next_department
        db.commit()

        new_task = Task(
            request_id=req.id,
            department=next_department,
        )
        from app.services.workflow_engine import SLA_LIMITS
        from datetime import timedelta
        if next_department in SLA_LIMITS:
            new_task.due_at = datetime.datetime.utcnow() + timedelta(seconds=SLA_LIMITS[next_department])

        db.add(new_task)
        db.commit()

        log = AuditLog(
            request_id=req.id,
            action="Task Completed",
            performed_by=current_user.email,
            department=current_user.role,
        )
        db.add(log)
        db.commit()

        return {"message": f"Moved to {next_department}"}
    else:
        req.status = "Completed"
        db.commit()

        log = AuditLog(
            request_id=req.id,
            action="Workflow Completed",
            performed_by=current_user.email,
            department=current_user.role,
        )
        db.add(log)
        db.commit()

        return {"message": "Workflow Completed"}
