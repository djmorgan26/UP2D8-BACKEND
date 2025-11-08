---
type: pattern
name: MongoDB Integration with FastAPI
status: implemented
created: 2025-11-08
updated: 2025-11-08
files:
  - dependencies.py
  - api/users.py
  - api/chat.py
  - api/feedback.py
  - api/analytics.py
related:
  - .ai/knowledge/patterns/azure-key-vault-integration.md
  - .ai/knowledge/components/dependencies.md
tags: [mongodb, database, fastapi, dependency-injection, pymongo]
---

# MongoDB Integration with FastAPI

## What It Is

A dependency injection pattern for integrating MongoDB with FastAPI using PyMongo. Provides database connections as FastAPI dependencies with automatic connection management and error handling.

## How It Works

The pattern uses FastAPI's dependency injection system to provide MongoDB database clients to route handlers.

**Key files:**
- `dependencies.py:38-52` - Database dependency function
- `api/users.py:18` - Example usage with `Depends(get_db_client)`
- `api/chat.py:30` - Example usage in chat endpoints

### Database Dependency (dependencies.py)

```python
async def get_db_client():
    """Dependency to get a MongoDB database client."""
    secrets = initialize_secrets()  # Get connection string from Key Vault
    mongo_connection_string = secrets["MONGO_DB_CONNECTION_STRING"]
    client = None
    try:
        client = MongoClient(mongo_connection_string)
        db = client.up2d8  # Select 'up2d8' database
        yield db
    except ConnectionFailure as e:
        print(f"MongoDB connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to MongoDB"
        )
    finally:
        if client:
            client.close()  # Always close connection
```

**Key features:**
- **Async generator**: Uses `yield` for dependency injection
- **Connection string from Key Vault**: No credentials in code
- **Automatic cleanup**: `finally` block ensures connection closes
- **Error handling**: Converts MongoDB errors to HTTP 500 responses
- **Database selection**: Returns `up2d8` database object

### Usage in Route Handlers

```python
@router.post("/api/users", status_code=status.HTTP_200_OK)
async def create_user(user: UserCreate, db=Depends(get_db_client)):
    users_collection = db.users  # Access 'users' collection
    existing_user = users_collection.find_one({"email": user.email})
    # ... rest of logic
```

**Pattern:**
1. Add `db=Depends(get_db_client)` to function signature
2. FastAPI injects database object
3. Access collections via `db.collection_name`
4. Connection automatically closed after request

### Collections Used

The application uses these MongoDB collections:

- **users**: User accounts and preferences
- **sessions**: Chat sessions with embedded messages
- **feedback**: User feedback on AI responses
- **analytics**: Application usage events

### Common Operations

**Insert:**
```python
users_collection.insert_one(new_user)
```

**Find:**
```python
user = users_collection.find_one({"user_id": user_id})
sessions = list(sessions_collection.find({"user_id": user_id}))
```

**Update:**
```python
users_collection.update_one(
    {"user_id": user_id},
    {"$set": update_fields, "$currentDate": {"updated_at": True}}
)
```

**Delete:**
```python
result = users_collection.delete_one({"user_id": user_id})
```

**Array operations:**
```python
# Add to array with deduplication
users_collection.update_one(
    {"email": user.email},
    {"$addToSet": {"topics": {"$each": user.topics}}}
)

# Push to array
sessions_collection.update_one(
    {"session_id": session_id},
    {"$push": {"messages": message_object}}
)
```

## Important Decisions

- **PyMongo over Motor**: Using synchronous PyMongo instead of async Motor (simpler, sufficient for current scale)
- **Connection per Request**: New connection for each request (simple, works for low-medium traffic)
- **Database Name**: Hard-coded `up2d8` database (could be configurable)
- **No Connection Pooling**: Relying on MongoClient's default pooling
- **Re-initialize Secrets**: Calls `initialize_secrets()` each time to ensure fresh connection string
- **Cosmos DB Compatible**: Connection string is for Azure Cosmos DB (MongoDB API)
- **No ORM**: Direct PyMongo calls instead of ODM like MongoEngine (more control, less abstraction)
- **Exclude _id**: Most queries exclude MongoDB's internal `_id` field from responses

## Usage Example

### Basic CRUD Operations

```python
from fastapi import APIRouter, Depends
from dependencies import get_db_client

router = APIRouter()

@router.post("/api/items")
async def create_item(item: dict, db=Depends(get_db_client)):
    # Access collection
    items = db.items

    # Insert document
    items.insert_one(item)

    return {"message": "Item created"}

@router.get("/api/items/{item_id}")
async def get_item(item_id: str, db=Depends(get_db_client)):
    items = db.items

    # Find document, exclude _id
    item = items.find_one({"item_id": item_id}, {"_id": 0})

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item

@router.put("/api/items/{item_id}")
async def update_item(item_id: str, updates: dict, db=Depends(get_db_client)):
    items = db.items

    # Update document
    result = items.update_one(
        {"item_id": item_id},
        {"$set": updates}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"message": "Item updated"}

@router.delete("/api/items/{item_id}")
async def delete_item(item_id: str, db=Depends(get_db_client)):
    items = db.items

    # Delete document
    result = items.delete_one({"item_id": item_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"message": "Item deleted"}
```

### Advanced Queries

```python
# Find with multiple conditions
users = list(db.users.find({
    "topics": {"$in": ["technology"]},
    "created_at": {"$gte": datetime(2025, 1, 1)}
}))

# Update with operators
db.sessions.update_one(
    {"session_id": session_id},
    {
        "$push": {"messages": message},
        "$inc": {"message_count": 1},
        "$currentDate": {"updated_at": True}
    }
)

# Aggregation
pipeline = [
    {"$match": {"user_id": user_id}},
    {"$group": {"_id": "$event_type", "count": {"$sum": 1}}}
]
results = list(db.analytics.aggregate(pipeline))
```

## Common Issues

- **Connection String Invalid**: Ensure Cosmos DB connection string is correctly retrieved from Key Vault
- **Database Not Created**: MongoDB/Cosmos DB creates database on first insert (lazy creation)
- **Collection Not Found**: Collections also created lazily on first insert
- **_id Field in Response**: Remember to exclude `{"_id": 0}` in find operations
- **Connection Not Closed**: Dependency injection handles cleanup automatically
- **Async vs Sync**: PyMongo is sync, wrapped in async functions (works but not fully async)

## Testing

- Test files: `tests/`
- Testing approach:
  - Mock `get_db_client` dependency for unit tests
  - Use MongoDB in-memory server for integration tests
  - Test connection failure scenarios

## Comparison with Alternatives

### Motor (Async PyMongo)
- ✅ Fully async operations
- ❌ More complex, overkill for current scale
- 📝 Could migrate if performance becomes issue

### MongoEngine/Beanie (ODM)
- ✅ Schema validation, models
- ❌ More abstraction, less control
- 📝 Current approach chosen for flexibility

### Connection Pooling Libraries
- Current: PyMongo's built-in pooling
- Alternative: Custom pool management
- 📝 Built-in sufficient for now

## Related Knowledge

- [Azure Key Vault Integration](./azure-key-vault-integration.md) - Where connection string comes from
- [Dependencies Component](../components/dependencies.md)
- [User Management](../features/user-management.md)
- [Chat API](../features/chat-api.md)

## Best Practices

✅ **DO:**
- Use `Depends(get_db_client)` in all route handlers
- Exclude `_id` field from API responses
- Check `matched_count`/`deleted_count` after operations
- Use UTC timestamps for all datetime fields
- Use MongoDB operators ($set, $push, $addToSet) appropriately

❌ **DON'T:**
- Create MongoClient instances manually
- Leave connections open
- Hard-code database/collection names everywhere
- Return MongoDB ObjectIds in API responses
- Store connection string in code

## Future Ideas

- [ ] Migrate to Motor for fully async MongoDB operations
- [ ] Implement connection pooling optimization
- [ ] Add database health check endpoint
- [ ] Implement database migration system
- [ ] Add MongoDB indexes for performance
- [ ] Create database models/schemas with Pydantic
- [ ] Add query result pagination
- [ ] Implement soft deletes with timestamps
- [ ] Add database transaction support
- [ ] Create database seeding scripts for testing
- [ ] Add MongoDB performance monitoring
- [ ] Implement read replicas for scaling
