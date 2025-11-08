---
type: feature
name: Chat API with Gemini Integration
status: implemented
created: 2025-11-08
updated: 2025-11-08
files:
  - api/chat.py
  - main.py
related:
  - .ai/knowledge/patterns/gemini-api-integration.md
  - .ai/knowledge/features/session-management.md
tags: [chat, gemini, ai, api, messaging]
---

# Chat API with Gemini Integration

## What It Does

Provides AI-powered chat functionality through Google Gemini API, allowing users to send prompts and receive AI-generated responses. Supports both simple chat requests and full session-based message management with persistent storage in MongoDB.

## How It Works

The chat API provides two distinct modes of operation:

### Simple Chat (POST /api/chat)
Direct proxy to Gemini API for one-off chat requests without session persistence.

**Key files:**
- `api/chat.py:20-27` - Chat endpoint that proxies requests to Gemini Pro model
- `main.py:30` - Gemini API configured with API key from Azure Key Vault

**Flow:**
1. Client sends POST request with `prompt` in request body
2. Endpoint creates Gemini Pro model instance
3. Generates content using `model.generate_content()`
4. Returns response text with empty sources array
5. Errors are caught and returned as HTTP 500 with detail message

### Session-Based Messaging
Full conversation management with MongoDB persistence for multi-turn conversations.

**Key files:**
- `api/chat.py:29-41` - Create new chat session
- `api/chat.py:43-47` - Get all sessions for a user
- `api/chat.py:49-58` - Send message to session
- `api/chat.py:60-66` - Retrieve messages from session

**Flow:**
1. **Create Session**: Client creates session with `user_id` and `title`
2. **Send Messages**: Messages pushed to session's message array in MongoDB
3. **Retrieve History**: Full message history retrieved by `session_id`
4. **User Sessions**: Get all sessions for a specific user

## Important Decisions

- **Gemini Pro Model**: Using `gemini-pro` model for general-purpose chat (not multimodal)
- **Session Storage**: Sessions stored in MongoDB with embedded messages array (not separate collection)
- **UUID Generation**: Using Python's `uuid.uuid4()` for globally unique session IDs
- **UTC Timestamps**: All timestamps use `datetime.now(UTC)` for consistency across timezones
- **Simple Chat Endpoint**: Kept separate from session-based chat for simple use cases that don't need persistence

## Usage Example

### Simple Chat
```python
# Request
POST /api/chat
{
  "prompt": "What is the capital of France?"
}

# Response
{
  "text": "The capital of France is Paris.",
  "sources": []
}
```

### Session-Based Chat
```python
# 1. Create session
POST /api/sessions
{
  "user_id": "user-123",
  "title": "Paris Questions"
}
# Returns: {"session_id": "abc-def-ghi"}

# 2. Send message
POST /api/sessions/abc-def-ghi/messages
{
  "content": "What is the capital of France?"
}
# Returns: {"message": "Message sent."}

# 3. Get messages
GET /api/sessions/abc-def-ghi/messages
# Returns: [{"role": "user", "content": "What is...", "timestamp": "..."}]

# 4. Get user's sessions
GET /api/users/user-123/sessions
# Returns: [{session_id, user_id, title, created_at, messages}]
```

## Testing

- Test files: `tests/`
- Coverage: Part of 20 passing tests
- Key test cases:
  - Successful chat response from Gemini
  - Error handling for Gemini API failures
  - Session creation with valid user_id
  - Message persistence in sessions
  - Session retrieval by user_id
  - Message retrieval by session_id
  - 404 handling for non-existent sessions

## Common Issues

- **Gemini API Errors**: If Gemini API key is invalid or expired, all chat requests fail with 500 error
- **Session Not Found**: Sending messages to non-existent session returns 404
- **MongoDB Connection**: If MongoDB is unreachable, session operations fail but simple chat still works
- **Sources Field**: Currently returns empty array, may need implementation if search grounding is added

## Related Knowledge

- [Session Management](./session-management.md) - Full session lifecycle
- [Gemini API Integration Pattern](../patterns/gemini-api-integration.md)
- [MongoDB Integration Pattern](../patterns/mongodb-integration.md)
- [Dependencies Component](../components/dependencies.md)

## Future Ideas

- [ ] Implement search grounding to populate `sources` field
- [ ] Add streaming responses for better UX
- [ ] Support Gemini Pro Vision for multimodal chat
- [ ] Add rate limiting per user
- [ ] Implement message editing/deletion
- [ ] Add conversation summarization
- [ ] Support system prompts and conversation context
