from pydantic import BaseModel

class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    contact: str

class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    contact: str

    model_config = {
        "from_attributes": True
    }