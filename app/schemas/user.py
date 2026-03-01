from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    effective_department: str | None = None

    model_config = {"from_attributes": True}


class UserMeResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    effective_department: str | None = None