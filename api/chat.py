from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    prompt: str

class SessionCreate(BaseModel):
    user_id: str
    title: str

class MessageContent(BaseModel):
    content: str

@router.post("/api/chat", status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest):
    # Placeholder for chat logic
    return {"text": "This is a mocked response."}

@router.post("/api/sessions", status_code=status.HTTP_200_OK)
async def create_session(session_data: SessionCreate):
    # Placeholder for session creation logic
    return {"session_id": "mock_session_id"}

@router.get("/api/users/{user_id}/sessions", status_code=status.HTTP_200_OK)
async def get_sessions(user_id: str):
    # Placeholder for getting sessions logic
    return [{
        "session_id": "mock_session_id",
        "user_id": user_id,
        "title": "Mock Session",
        "created_at": "2023-01-01T00:00:00Z"
    }]

@router.post("/api/sessions/{session_id}/messages", status_code=status.HTTP_200_OK)
async def send_message(session_id: str, message_content: MessageContent):
    # Placeholder for sending message logic
    return {"message": "Message sent."}

@router.get("/api/sessions/{session_id}/messages", status_code=status.HTTP_200_OK)
async def get_messages(session_id: str):
    # Placeholder for getting messages logic
    return [
        {"role": "user", "content": "Hello"},
        {"role": "model", "content": "This is a mocked response."}
    ]
