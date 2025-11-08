---
type: feature
name: User Management
status: implemented
created: 2025-11-08
updated: 2025-11-08
files:
  - api/users.py
  - main.py
related:
  - .ai/knowledge/patterns/mongodb-integration.md
  - .ai/knowledge/components/dependencies.md
tags: [users, crud, mongodb, email, preferences]
---

# User Management

## What It Does

Provides complete CRUD (Create, Read, Update, Delete) operations for user accounts in the UP2D8 system. Handles user subscriptions with email validation, topic preferences, and custom user preferences with automatic deduplication.

## How It Works

The user management system provides a full REST API for managing user data stored in MongoDB.

**Key files:**
- `api/users.py:17-42` - Create user (POST /api/users)
- `api/users.py:44-65` - Update user preferences (PUT /api/users/{user_id})
- `api/users.py:67-73` - Get user by ID (GET /api/users/{user_id})
- `api/users.py:75-81` - Delete user (DELETE /api/users/{user_id})
- `main.py:38` - User router registration

### Create User (POST /api/users)

**Flow:**
1. Client sends email (validated as EmailStr) and topics list
2. Check if user with email already exists in MongoDB
3. If exists: Add new topics to existing user's topics array (deduplicated with `$addToSet`)
4. If new: Generate UUID, create user document with email, topics, and timestamp
5. Return success message and user_id

**Important behavior:** Upsert pattern - won't create duplicates, just updates existing users

### Update User (PUT /api/users/{user_id})

**Flow:**
1. Client sends optional `topics` and/or `preferences` dict
2. Build update_fields dict with only provided fields
3. Validate at least one field is provided (400 error if empty)
4. Update user document with `$set` and `$currentDate` for updated_at
5. Return 404 if user_id not found, otherwise success

### Get User (GET /api/users/{user_id})

**Flow:**
1. Query MongoDB by user_id
2. Exclude MongoDB's internal `_id` field from response
3. Return 404 if not found, otherwise full user document

### Delete User (DELETE /api/users/{user_id})

**Flow:**
1. Delete user document by user_id
2. Check deleted_count to determine if user existed
3. Return 404 if not found, otherwise success message

## Important Decisions

- **Email as Unique Identifier**: Email field must be unique, enforced by find_one checks
- **UUID for user_id**: Using UUIDs instead of MongoDB ObjectIds for client-friendly IDs
- **Pydantic EmailStr**: Automatic email validation at the model level
- **Upsert on Create**: POST /api/users acts as upsert - updates if exists, creates if new
- **Flexible Preferences**: `preferences` field is a dict for extensibility (no fixed schema)
- **Topic Deduplication**: Using `$addToSet` with `$each` to prevent duplicate topics
- **Soft vs Hard Delete**: Currently hard deletes - could be changed to soft delete pattern
- **UTC Timestamps**: All timestamps use UTC for consistency

## Usage Example

### Create User
```python
POST /api/users
{
  "email": "user@example.com",
  "topics": ["technology", "science"]
}

# Response (new user)
{
  "message": "Subscription confirmed.",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}

# Response (existing user)
{
  "message": "User already exists, topics updated.",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### Update User Preferences
```python
PUT /api/users/a1b2c3d4-e5f6-7890-abcd-ef1234567890
{
  "topics": ["technology", "AI", "health"],
  "preferences": {
    "newsletter_frequency": "weekly",
    "theme": "dark"
  }
}

# Response
{
  "message": "Preferences updated."
}
```

### Get User
```python
GET /api/users/a1b2c3d4-e5f6-7890-abcd-ef1234567890

# Response
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "user@example.com",
  "topics": ["technology", "AI", "health"],
  "preferences": {
    "newsletter_frequency": "weekly",
    "theme": "dark"
  },
  "created_at": "2025-11-08T10:30:00Z",
  "updated_at": "2025-11-08T11:45:00Z"
}
```

### Delete User
```python
DELETE /api/users/a1b2c3d4-e5f6-7890-abcd-ef1234567890

# Response
{
  "message": "User deleted."
}
```

## Testing

- Test files: `tests/`
- Coverage: Part of 20 passing tests
- Key test cases:
  - Create new user with valid email
  - Create user with existing email (upsert)
  - Email validation failures
  - Update user topics
  - Update user preferences
  - Update with empty request body (400 error)
  - Get existing user
  - Get non-existent user (404)
  - Delete existing user
  - Delete non-existent user (404)

## Common Issues

- **Email Validation**: Invalid emails are rejected by Pydantic before reaching handler
- **User Not Found**: 404 errors indicate user_id doesn't exist in database
- **Empty Updates**: PUT requests with no fields will return 400 error
- **Topic Duplicates**: Same topic added multiple times will only appear once (deduplicated)
- **Preferences Overwrite**: Entire preferences dict is replaced, not merged

## Related Knowledge

- [MongoDB Integration Pattern](../patterns/mongodb-integration.md)
- [Dependencies Component](../components/dependencies.md)
- [Session Management](./session-management.md)

## Future Ideas

- [ ] Add user authentication (OAuth, JWT)
- [ ] Implement soft delete with `deleted_at` field
- [ ] Add email verification workflow
- [ ] Implement user roles/permissions
- [ ] Add pagination for user lists
- [ ] Merge preferences instead of replace
- [ ] Add user activity tracking
- [ ] Support bulk user operations
- [ ] Add user search/filtering
- [ ] Implement email uniqueness constraint at DB level
