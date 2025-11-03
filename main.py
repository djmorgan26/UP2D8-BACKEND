import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, status
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
from shared.key_vault_client import KeyVaultClient

from api.analytics import router as analytics_router
from api.chat import router as chat_router
from api.feedback import router as feedback_router
from api.users import router as users_router

# Load environment variables from .env file
load_dotenv()

# Global variables to hold initialized clients and secrets
key_vault_client: KeyVaultClient = None
MONGO_DB_CONNECTION_STRING: str = None
GEMINI_API_KEY: str = None
SMTP_KEY: str = None
GOOGLE_CLIENT_ID: str = None
GOOGLE_CLIENT_SECRET: str = None
client: MongoClient = None
db = None

def get_key_vault_client_instance():
    global key_vault_client
    if key_vault_client is None:
        key_vault_client = KeyVaultClient()
    return key_vault_client

def get_mongo_client_instance(connection_string: str):
    global client, db
    if client is None:
        client = MongoClient(connection_string)
        db = client.up2d8
    return client

def initialize_secrets():
    global MONGO_DB_CONNECTION_STRING, GEMINI_API_KEY, SMTP_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
    kv_client = get_key_vault_client_instance()
    MONGO_DB_CONNECTION_STRING = kv_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8")
    GEMINI_API_KEY = kv_client.get_secret("UP2D8-GEMINI-API-Key")
    SMTP_KEY = kv_client.get_secret("UP2D8-SMTP-KEY")
    GOOGLE_CLIENT_ID = kv_client.get_secret("GOOGLE-CLIENT-ID")
    GOOGLE_CLIENT_SECRET = kv_client.get_secret("GOOGLE-CLIENT-SECRET")
    genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI()

app.include_router(analytics_router)
app.include_router(chat_router)
app.include_router(feedback_router)
app.include_router(users_router)

@app.on_event("startup")
async def startup_db_client():
    initialize_secrets()
    try:
        mongo_client = get_mongo_client_instance(MONGO_DB_CONNECTION_STRING)
        mongo_client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except ConnectionFailure as e:
        print(f"MongoDB connection failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to connect to MongoDB")

@app.on_event("shutdown")
async def shutdown_db_client():
    global client
    if client:
        client.close()

@app.get("/")
def read_root():
    return {"Hello": "World"}