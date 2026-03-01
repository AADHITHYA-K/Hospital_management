from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserMeResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_db, get_current_user
from app.services.workflow_engine import get_user_department

router = APIRouter(prefix="/auth", tags=["Authentication"])

VALID_ROLES = {"Admin", "Doctor", "Nurse", "Lab Technician", "Billing Officer", "OPD", "Lab", "Radiology", "Anesthesia", "OT", "ICU", "Billing"}

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if user.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Allowed: {', '.join(sorted(VALID_ROLES))}",
        )
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role=user.role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.id}


@router.get("/me", response_model=UserMeResponse)
def me(current_user=Depends(get_current_user)):
    return UserMeResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        effective_department=get_user_department(current_user.role),
    )

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.email})

    return {"access_token": token, "token_type": "bearer"}