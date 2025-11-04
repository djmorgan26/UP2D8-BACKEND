import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, status
from dotenv import load_dotenv

from api.analytics import router as analytics_router
from api.chat import router as chat_router
from api.feedback import router as feedback_router
from api.users import router as users_router

from dependencies import initialize_secrets, get_db_client

# Load environment variables from .env file
load_dotenv()

# Global variables to hold initialized secrets
GEMINI_API_KEY: str = None
SMTP_KEY: str = None
GOOGLE_CLIENT_ID: str = None
GOOGLE_CLIENT_SECRET: str = None

# Initialize secrets at module level for global access (e.g., by genai.configure)
secrets = initialize_secrets()
GEMINI_API_KEY = secrets["GEMINI_API_KEY"]
SMTP_KEY = secrets["SMTP_KEY"]
GOOGLE_CLIENT_ID = secrets["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = secrets["GOOGLE_CLIENT_SECRET"]
genai.configure(api_key=GEMINI_API_KEY)


app = FastAPI()

app.include_router(analytics_router)
app.include_router(chat_router)
app.include_router(feedback_router)
app.include_router(users_router)



@app.get("/")
def read_root():
    return {"Hello": "World"}