# Inter-Department Workflow Automation System

Medical & Healthcare Backend – request routing, tracking, SLA monitoring, and audit trail.

## Setup

1. **Python 3.10+** and **PostgreSQL** required.

2. Create a database:
   ```bash
   createdb hospital_db
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Set environment variables or edit `app/config.py`:
   - `DATABASE_URL` – PostgreSQL connection string
   - `SECRET_KEY` – JWT secret

5. Run the backend:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. Open in browser: **http://localhost:8000**  
   - Redirects to the frontend at `/static/index.html`.  
   - API docs: **http://localhost:8000/docs**

## API Overview

| Area | Endpoints |
|------|-----------|
| **Auth** | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| **Patients** | `POST /patients/`, `GET /patients/`, `GET /patients/{id}` |
| **Requests** | `POST /requests/`, `GET /requests/`, `GET /requests/{id}`, `GET /requests/{id}/status`, `GET /requests/{id}/tasks`, `POST /requests/{id}/complete` |
| **Tasks** | `GET /tasks/my-tasks`, `GET /tasks/sla-breaches` |
| **Workflows** | `GET /workflows/definitions` |
| **Audit** | `GET /audit/request/{request_id}` |
| **Analytics** | `GET /analytics/department-performance` (Admin only) |

## Roles

- **Admin** – Full access, including Analytics.
- **Doctor, Nurse, Lab Technician, Billing Officer** – Staff roles.
- **OPD, Lab, Radiology, Anesthesia, OT, ICU, Billing** – Department roles (for task assignment).

## Workflows

- **LabTest**: OPD → Lab → Doctor  
- **Radiology**: OPD → Radiology → Doctor  
- **Surgery**: OPD → Lab → Anesthesia → OT → ICU → Billing  
- **Insurance Approval**: OPD → Billing → Doctor  
- **Discharge**: OPD → Lab → Billing → Doctor  

SLA limits (seconds) per department are exposed at `GET /workflows/definitions`.
