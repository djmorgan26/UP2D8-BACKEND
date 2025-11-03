from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, EmailStr
import uuid

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    topics: list[str]

class UserUpdate(BaseModel):
    topics: list[str] | None = None
    preferences: dict | None = None

@router.post("/api/users", status_code=status.HTTP_200_OK)
async def create_user(user: UserCreate):
    # Placeholder for user creation logic
    user_id = str(uuid.uuid4())
    return {"message": "Subscription confirmed.", "user_id": user_id}

@router.put("/api/users/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(user_id: str, user_update: UserUpdate):
    # Placeholder for user update logic
    return {"message": "Preferences updated."}
