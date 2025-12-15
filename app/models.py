from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    cnic: str
    password: str
    role: UserRole = UserRole.USER

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    cnic: str
    role: UserRole
    created_at: str
    
    class Config:
        from_attributes = True

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    review_text: str
    sentiment_results: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AdminReviewResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    user_email: str
    review_text: str
    sentiment_results: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True