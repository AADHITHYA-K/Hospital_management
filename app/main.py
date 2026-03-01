from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.database import init_db
import app.models.user
import app.models.patient
from app.routes import patient
from app.routes import auth
import app.models.request
import app.models.task
import app.models.audit
from app.core.dependencies import get_current_user
from app.routes import request
from app.routes import task
from app.routes import analytics
from app.routes import workflow
from app.routes import audit

app = FastAPI(
    title="Inter-Department Workflow Automation System",
    description="Medical & Healthcare Backend – request routing, tracking, SLA, audit.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create tables / apply simple schema corrections before the app starts
init_db()

app.include_router(analytics.router)
app.include_router(request.router)
app.include_router(auth.router)
app.include_router(patient.router)
app.include_router(task.router)
app.include_router(workflow.router)
app.include_router(audit.router)

from fastapi.staticfiles import StaticFiles
from pathlib import Path

_frontend = Path(__file__).resolve().parent.parent / "frontend"
if _frontend.exists():
    app.mount("/static", StaticFiles(directory=_frontend), name="static")


@app.get("/")
def root():
    if _frontend.exists():
        return RedirectResponse(url="/static/index.html")
    return {"message": "Backend Connected to PostgreSQL Successfully", "docs": "/docs"}


@app.get("/protected")
def protected_route(current_user=Depends(get_current_user)):
    return {
        "message": "You are authorized",
        "user": current_user.email,
        "role": current_user.role,
    }
