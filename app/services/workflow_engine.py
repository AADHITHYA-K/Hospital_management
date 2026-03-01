# Maps user roles to workflow departments (for task completion & my-tasks)
# Staff roles like "Lab Technician" work in "Lab" department
ROLE_TO_DEPARTMENT = {
    "Lab Technician": "Lab",
    "Billing Officer": "Billing",
    "Doctor": "Doctor",
    "Nurse": "OPD",
    "OPD": "OPD",
    "Lab": "Lab",
    "Radiology": "Radiology",
    "Anesthesia": "Anesthesia",
    "OT": "OT",
    "ICU": "ICU",
    "Billing": "Billing",
}


def get_user_department(role: str) -> str | None:
    """Return the department this role can complete tasks for, or None if not a department role."""
    if role == "Admin":
        return None
    return ROLE_TO_DEPARTMENT.get(role, role)


def can_user_complete_department(user_role: str, department: str) -> bool:
    """Check if a user with this role can complete tasks for this department."""
    user_dept = get_user_department(user_role)
    return user_dept == department if user_dept else False


# Request types and their department sequence (per project description)
WORKFLOWS = {
    "LabTest": ["OPD", "Lab", "Doctor"],
    "Radiology": ["OPD", "Radiology", "Doctor"],
    "Surgery": ["OPD", "Lab", "Anesthesia", "OT", "ICU", "Billing"],
    "Insurance Approval": ["OPD", "Billing", "Doctor"],
    "Discharge": ["OPD", "Lab", "Billing", "Doctor"],
}
SLA_LIMITS = {
    "OPD": 300,
    "Lab": 600,
    "Radiology": 900,
    "Doctor": 900,
    "Anesthesia": 600,
    "OT": 1200,
    "ICU": 1800,
    "Billing": 600,
}
def get_next_department(request_type, current_department):
    steps = WORKFLOWS.get(request_type)

    if not steps:
        return None

    if current_department in steps:
        index = steps.index(current_department)
        if index + 1 < len(steps):
            return steps[index + 1]

    return None