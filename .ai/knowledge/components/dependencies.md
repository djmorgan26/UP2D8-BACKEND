---
type: component
name: Dependencies Module
status: implemented
created: 2025-11-08
updated: 2025-11-08
files:
  - dependencies.py
  - shared/key_vault_client.py
related:
  - .ai/knowledge/patterns/azure-key-vault-integration.md
  - .ai/knowledge/patterns/mongodb-integration.md
tags: [dependencies, fastapi, dependency-injection, secrets, database]
---

# Dependencies Module

## What It Is

The central dependency management module for the UP2D8 backend. Provides FastAPI dependencies for database connections and manages application secrets retrieved from Azure Key Vault. Acts as the glue between Key Vault, MongoDB, and the API routes.

## How It Works

The dependencies module provides two primary functions:

1. **Secret Management**: Initialize and access secrets from Azure Key Vault
2. **Database Dependency**: Provide MongoDB database connections to route handlers

**Key files:**
- `dependencies.py` - Main dependencies module
- `shared/key_vault_client.py` - Key Vault client wrapper

### Module Structure

```python
# Global variables for secrets
GEMINI_API_KEY: str = None
SMTP_KEY: str = None
GOOGLE_CLIENT_ID: str = None
GOOGLE_CLIENT_SECRET: str = None

# Functions
get_key_vault_client_instance()    # Factory for KeyVaultClient
initialize_secrets()               # Load all secrets from Key Vault
async get_db_client()             # FastAPI dependency for MongoDB
```

### Secret Management Functions

**get_key_vault_client_instance() (dependencies.py:18-19)**
```python
def get_key_vault_client_instance():
    return KeyVaultClient()
```
- Simple factory function for creating KeyVaultClient instances
- Used by `initialize_secrets()` to access Key Vault

**initialize_secrets() (dependencies.py:21-36)**
```python
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
```

**Purpose:**
- Retrieve all application secrets from Azure Key Vault
- Populate global variables for library configuration (genai)
- Return dict of secrets for other uses
- Configure Gemini API with retrieved key

**Called from:**
- `main.py:25` - At application startup
- `dependencies.py:40` - In `get_db_client()` for fresh connection string

### Database Dependency

**async get_db_client() (dependencies.py:38-52)**
```python
async def get_db_client():
    """Dependency to get a MongoDB database client."""
    secrets = initialize_secrets()  # Re-initialize for fresh connection string
    mongo_connection_string = secrets["MONGO_DB_CONNECTION_STRING"]
    client = None
    try:
        client = MongoClient(mongo_connection_string)
        db = client.up2d8  # Select database
        yield db
    except ConnectionFailure as e:
        print(f"MongoDB connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to MongoDB"
        )
    finally:
        if client:
            client.close()
```

**Purpose:**
- Provide MongoDB database as FastAPI dependency
- Manage connection lifecycle (open/close)
- Handle connection errors gracefully
- Ensure connections are always closed

**Used by:**
- All API routes that need database access
- Example: `api/users.py:18` - `db=Depends(get_db_client)`

## Important Decisions

- **Global Variables**: Some secrets stored globally for libraries requiring module-level config
- **Re-initialize in get_db_client**: Calls `initialize_secrets()` each time to ensure fresh secrets
- **Synchronous Secrets**: Secret retrieval is synchronous (not async)
- **Module-Level Imports**: genai configured at module level for global access
- **Single Database**: Hard-coded to `up2d8` database
- **Connection per Request**: New MongoDB connection for each request (simple pattern)
- **Error Propagation**: Exceptions from Key Vault propagate to caller
- **No Connection Pooling Config**: Using PyMongo's default connection pool

## Architecture Diagram

```
┌─────────────────┐
│   main.py       │
│  (startup)      │
└────────┬────────┘
         │
         │ initialize_secrets()
         ▼
┌─────────────────────────┐
│  dependencies.py        │
│                         │
│  ┌────────────────────┐ │
│  │ Global Secrets     │ │
│  │ - GEMINI_API_KEY   │ │
│  │ - SMTP_KEY         │ │
│  │ - GOOGLE_*         │ │
│  └────────────────────┘ │
│                         │
│  get_db_client()        │←─── FastAPI routes
└────────┬────────────────┘
         │
         ├─────────────────────┐
         │                     │
         ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│ KeyVaultClient   │  │  MongoClient     │
│ (Azure KV)       │  │  (MongoDB)       │
└──────────────────┘  └──────────────────┘
```

## Usage Example

### Using Secrets

```python
# In main.py (startup)
from dependencies import initialize_secrets

secrets = initialize_secrets()
# Gemini API is now configured globally
# Global variables are populated

# In other modules
from dependencies import GEMINI_API_KEY, SMTP_KEY

# Use the global variables
print(f"API Key loaded: {GEMINI_API_KEY[:5]}...")
```

### Using Database Dependency

```python
from fastapi import APIRouter, Depends
from dependencies import get_db_client

router = APIRouter()

@router.post("/api/items")
async def create_item(item: dict, db=Depends(get_db_client)):
    # db is automatically injected by FastAPI
    # Connection is automatically managed (opened/closed)

    items_collection = db.items
    items_collection.insert_one(item)

    return {"message": "Item created"}
    # Connection automatically closed after response
```

### Testing with Dependency Override

```python
from fastapi.testclient import TestClient
from main import app
from dependencies import get_db_client

# Mock database for testing
def mock_db_client():
    # Return mock database
    yield MockDatabase()

app.dependency_overrides[get_db_client] = mock_db_client

client = TestClient(app)
response = client.post("/api/items", json={"name": "test"})
```

## Common Issues

- **Secrets Not Loaded**: Ensure `initialize_secrets()` called at startup
- **Azure Login Required**: Local dev requires `az login` for Key Vault access
- **Connection String Refresh**: `get_db_client()` re-initializes secrets each time
- **Global Variables None**: If `initialize_secrets()` not called, globals remain None
- **MongoDB Connection Timeout**: Check network access to Cosmos DB
- **Circular Imports**: Be careful importing from dependencies.py

## Testing

- Test files: `tests/`
- Testing approach:
  - Mock `get_key_vault_client_instance()` for secret tests
  - Mock `get_db_client()` for database tests
  - Use dependency overrides in FastAPI tests
  - Test connection failure scenarios

## Secrets Loaded

The module manages these secrets from Azure Key Vault:

| Local Variable | Key Vault Secret Name | Purpose |
|----------------|----------------------|---------|
| MONGO_DB_CONNECTION_STRING | COSMOS-DB-CONNECTION-STRING-UP2D8 | Cosmos DB connection |
| GEMINI_API_KEY | UP2D8-GEMINI-API-Key | Google Gemini API |
| SMTP_KEY | UP2D8-SMTP-KEY | Email sending |
| GOOGLE_CLIENT_ID | GOOGLE-CLIENT-ID | OAuth authentication |
| GOOGLE_CLIENT_SECRET | GOOGLE-CLIENT-SECRET | OAuth authentication |

## Related Knowledge

- [Azure Key Vault Integration Pattern](../patterns/azure-key-vault-integration.md)
- [MongoDB Integration Pattern](../patterns/mongodb-integration.md)
- [Chat API](../features/chat-api.md) - Uses database dependency
- [User Management](../features/user-management.md) - Uses database dependency

## Best Practices

✅ **DO:**
- Call `initialize_secrets()` at application startup
- Use `Depends(get_db_client)` for all database access
- Override dependencies for testing
- Handle connection failures gracefully

❌ **DON'T:**
- Access Key Vault directly in route handlers
- Create MongoClient instances manually
- Store secrets in environment variables
- Import global variables before initialization

## Future Ideas

- [ ] Add secret caching to reduce Key Vault calls
- [ ] Implement connection pooling configuration
- [ ] Create health check for dependencies
- [ ] Add retry logic for transient failures
- [ ] Implement graceful secret rotation
- [ ] Add dependency injection for Gemini client
- [ ] Create typed secret models with Pydantic
- [ ] Add metrics for connection pool usage
- [ ] Implement database read/write splitting
- [ ] Add circuit breaker for external dependencies
- [ ] Create dependency initialization middleware
- [ ] Add secret validation on startup
