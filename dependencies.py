from fastapi import HTTPException, status
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
from shared.key_vault_client import KeyVaultClient
import os
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Global variables to hold initialized secrets
GEMINI_API_KEY: str = None
SMTP_KEY: str = None
GOOGLE_CLIENT_ID: str = None
GOOGLE_CLIENT_SECRET: str = None

def get_key_vault_client_instance():
    return KeyVaultClient()

def initialize_secrets():
    kv_client = get_key_vault_client_instance()
    secrets = {
        "MONGO_DB_CONNECTION_STRING": kv_client.get_secret("COSMOS-DB-CONNECTION-STRING-UP2D8"),
        "GEMINI_API_KEY": kv_client.get_secret("UP2D8-GEMINI-API-Key"),
        "SMTP_KEY": kv_client.get_secret("UP2D8-SMTP-KEY"),
        "GOOGLE_CLIENT_ID": kv_client.get_secret("GOOGLE-CLIENT-ID"),
        "GOOGLE_CLIENT_SECRET": kv_client.get_secret("GOOGLE-CLIENT-SECRET"),
    }
    global GEMINI_API_KEY, SMTP_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
    GEMINI_API_KEY = secrets["GEMINI_API_KEY"]
    SMTP_KEY = secrets["SMTP_KEY"]
    GOOGLE_CLIENT_ID = secrets["GOOGLE_CLIENT_ID"]
    GOOGLE_CLIENT_SECRET = secrets["GOOGLE_CLIENT_SECRET"]
    genai.configure(api_key=GEMINI_API_KEY)
    return secrets

async def get_db_client():
    """Dependency to get a MongoDB database client."""
    secrets = initialize_secrets() # Re-initialize secrets to ensure connection string is fresh
    mongo_connection_string = secrets["MONGO_DB_CONNECTION_STRING"]
    client = None
    try:
        client = MongoClient(mongo_connection_string)
        db = client.up2d8
        yield db
    except ConnectionFailure as e:
        print(f"MongoDB connection failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to connect to MongoDB")
    finally:
        if client:
            client.close()