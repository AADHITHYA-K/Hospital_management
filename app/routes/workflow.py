from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.services.workflow_engine import WORKFLOWS, SLA_LIMITS, ROLE_TO_DEPARTMENT

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.get("/definitions")
def list_workflows(current_user=Depends(get_current_user)):
    """Return workflow definitions: request type -> list of departments."""
    return {
        "workflows": WORKFLOWS,
        "sla_limits_seconds": SLA_LIMITS,
        "role_to_department": ROLE_TO_DEPARTMENT,
    }
