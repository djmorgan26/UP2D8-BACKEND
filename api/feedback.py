from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()

class FeedbackCreate(BaseModel):
    message_id: str
    user_id: str
    rating: str

@router.post("/api/feedback", status_code=status.HTTP_201_CREATED)
async def create_feedback(feedback: FeedbackCreate):
    # Placeholder for feedback logic
    return {"message": "Feedback received."}
