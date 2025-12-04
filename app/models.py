from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    cnic: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    cnic: str
    created_at: str
    
    class Config:
        orm_mode = True