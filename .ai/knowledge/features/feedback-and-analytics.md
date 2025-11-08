---
type: feature
name: Feedback and Analytics
status: implemented
created: 2025-11-08
updated: 2025-11-08
files:
  - api/feedback.py
  - api/analytics.py
  - main.py
related:
  - .ai/knowledge/patterns/mongodb-integration.md
  - .ai/knowledge/features/chat-api.md
tags: [feedback, analytics, tracking, monitoring, mongodb]
---

# Feedback and Analytics

## What It Does

Provides two complementary systems for collecting user behavior data and improving the UP2D8 application:

1. **Feedback System**: Collects user ratings on AI-generated chat messages
2. **Analytics System**: Tracks user events and interactions throughout the application

Both systems persist data to MongoDB for later analysis and product improvement.

## How It Works

### Feedback System (POST /api/feedback)

Captures user ratings on individual chat messages to measure AI response quality.

**Key files:**
- `api/feedback.py:13-23` - Feedback endpoint
- `main.py:37` - Feedback router registration

**Flow:**
1. Client sends `message_id`, `user_id`, and `rating` (string)
2. Create feedback document with timestamp (UTC)
3. Insert into MongoDB `feedback` collection
4. Return HTTP 201 Created with success message

**Data model:**
```python
{
  "message_id": str,  # ID of the chat message being rated
  "user_id": str,     # User providing feedback
  "rating": str,      # Rating value (e.g., "good", "bad", "1-5")
  "timestamp": datetime  # When feedback was given
}
```

### Analytics System (POST /api/analytics)

General-purpose event tracking for user behavior and application usage.

**Key files:**
- `api/analytics.py:13-23` - Analytics endpoint
- `main.py:35` - Analytics router registration

**Flow:**
1. Client sends `user_id`, `event_type`, and `details` dict
2. Create analytics document with timestamp (UTC)
3. Insert into MongoDB `analytics` collection
4. Return HTTP 202 Accepted with success message

**Data model:**
```python
{
  "user_id": str,        # User who triggered the event
  "event_type": str,     # Type of event (e.g., "page_view", "button_click")
  "details": dict,       # Flexible dict for event-specific data
  "timestamp": datetime  # When event occurred
}
```

## Important Decisions

- **Separate Collections**: Feedback and analytics stored in different MongoDB collections for easier querying
- **String Rating**: Rating field is string (not int) to allow flexible rating systems (thumbs up/down, 1-5 stars, etc.)
- **Flexible Details**: Analytics details is a dict to support any event schema without backend changes
- **HTTP Status Codes**:
  - Feedback returns 201 Created (resource created)
  - Analytics returns 202 Accepted (async processing, fire-and-forget)
- **No Validation on Rating**: Rating accepts any string value (could add enum constraint)
- **UTC Timestamps**: All timestamps use `datetime.now(UTC)` for consistency
- **No Read Endpoints**: Currently write-only APIs (no GET endpoints for querying feedback/analytics)
- **No Authentication**: Relies on client to provide correct user_id (should add auth)

## Usage Example

### Submit Feedback
```python
POST /api/feedback
{
  "message_id": "msg-123",
  "user_id": "user-456",
  "rating": "positive"
}

# Response
{
  "message": "Feedback received."
}
```

### Log Analytics Event
```python
# Page view event
POST /api/analytics
{
  "user_id": "user-456",
  "event_type": "page_view",
  "details": {
    "page": "/dashboard",
    "referrer": "/login",
    "duration_ms": 5000
  }
}

# Button click event
POST /api/analytics
{
  "user_id": "user-456",
  "event_type": "button_click",
  "details": {
    "button_id": "submit-chat",
    "context": "chat-interface"
  }
}

# Response
{
  "message": "Event logged."
}
```

## Testing

- Test files: `tests/`
- Coverage: Part of 20 passing tests
- Key test cases:
  - Submit valid feedback
  - Submit analytics event
  - Validate Pydantic models
  - MongoDB insertion success
  - Timestamp generation
  - Details dict flexibility

## Common Issues

- **No User Validation**: System doesn't verify user_id exists in users collection
- **No Message Validation**: System doesn't verify message_id exists (could reference non-existent message)
- **No Rating Constraints**: Any string accepted as rating (could be typo or invalid value)
- **No Deduplication**: Same feedback can be submitted multiple times for same message
- **MongoDB Connection**: If MongoDB is down, both endpoints fail silently

## Related Knowledge

- [Chat API](./chat-api.md) - Where message_id comes from
- [User Management](./user-management.md) - Where user_id comes from
- [MongoDB Integration Pattern](../patterns/mongodb-integration.md)
- [Dependencies Component](../components/dependencies.md)

## Future Ideas

- [ ] Add GET endpoints to retrieve feedback and analytics
- [ ] Implement feedback aggregation (avg rating per message/user)
- [ ] Add analytics dashboards/visualization
- [ ] Validate user_id and message_id against database
- [ ] Add rating enum constraint (e.g., "positive", "negative", "neutral")
- [ ] Implement deduplication (one feedback per user per message)
- [ ] Add batch analytics submission
- [ ] Support event filtering and querying
- [ ] Add analytics export functionality (CSV, JSON)
- [ ] Implement real-time analytics streaming
- [ ] Add feedback comments/text field
- [ ] Create analytics aggregation pipelines
- [ ] Add user privacy controls (opt-out of analytics)
- [ ] Implement data retention policies
