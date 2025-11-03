from fastapi import FastAPI, status
from pydantic import BaseModel
from typing import List

app = FastAPI()

class User(BaseModel):
    email: str
    topics: List[str]

class UserUpdate(BaseModel):
    topics: List[str]
    preferences: dict

class ChatPrompt(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    text: str
    sources: List[dict]

class Session(BaseModel):
    session_id: str
    title: str
    created_at: str

class Message(BaseModel):
    message_id: str
    role: str
    content: str
    timestamp: str

class NewMessage(BaseModel):
    content: str

class Feedback(BaseModel):
    message_id: str
    user_id: str
    rating: str

class AnalyticsEvent(BaseModel):
    user_id: str
    event_type: str
    details: dict

@app.post("/api/users")
def create_user(user: User):
    return {"message": "Subscription confirmed.", "user_id": "some_user_id"}

@app.put("/api/users/{user_id}")
def update_user(user_id: str, user: UserUpdate):
    return {"message": "Preferences updated."}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(prompt: ChatPrompt):
    # This is a stateless endpoint that proxies a prompt to the Gemini API with search grounding.
    # It does not persist messages.
    # This provides the core chat functionality.
    return {"text": "This is a response from the model.", "sources": [{"web": {"uri": "https://example.com", "title": "Example"}}]}

@app.get("/api/users/{user_id}/sessions", response_model=List[Session])
async def get_sessions(user_id: str):
    return [
        {
            "session_id": "some_session_id",
            "title": "Example Session",
            "created_at": "2025-11-03T12:00:00Z",
        }
    ]

@app.get("/api/sessions/{session_id}/messages", response_model=List[Message])
async def get_messages(session_id: str):
    return [
        {
            "message_id": "some_message_id",
            "role": "user",
            "content": "Hello",
            "timestamp": "2025-11-03T12:00:00Z",
        },
        {
            "message_id": "some_other_message_id",
            "role": "model",
            "content": "Hi there!",
            "timestamp": "2025-11-03T12:00:01Z",
        },
    ]

@app.post("/api/sessions/{session_id}/messages")
async def create_message(session_id: str, message: NewMessage):
    return {
        "user_message": {
            "message_id": "new_user_message_id",
            "role": "user",
            "content": message.content,
            "timestamp": "2025-11-03T12:00:02Z",
        },
        "model_message": {
            "message_id": "new_model_message_id",
            "role": "model",
            "content": "This is a new response from the model.",
            "timestamp": "2025-11-03T12:00:03Z",
        },
    }

@app.post("/api/feedback", status_code=status.HTTP_201_CREATED)
async def create_feedback(feedback: Feedback):
    return {"message": "Feedback received."}

@app.post("/api/analytics", status_code=status.HTTP_202_ACCEPTED)
async def create_analytics(event: AnalyticsEvent):
    return {"message": "Event logged."}

@app.get("/")
def read_root():
    return {"Hello": "World"}
