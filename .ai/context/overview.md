# Project Overview

**Project Name**: UP2D8 - Backend API Service
**Created**: 2025-11-08
**Status**: Active Development
**Repository**: UP2D8-BACKEND

---

## What This Is

A **FastAPI-based backend service** for the UP2D8 application. This service handles all live user requests from the frontend, manages database interactions with MongoDB, and securely calls the Google Gemini API with search grounding capabilities.

Think of it as the **central nervous system** of UP2D8 - it connects the frontend, database, and AI capabilities together with secure authentication.

---

## The Problem It Solves

### Core Challenges

The UP2D8 backend addresses several key challenges:

1. **Secure Secrets Management**: No secrets in code/env files - all managed via Azure Key Vault
2. **AI API Integration**: Secure proxy to Gemini API with search grounding
3. **Session Persistence**: Maintain chat history across user sessions in MongoDB
4. **User Management**: Handle user subscriptions, preferences, and analytics
5. **Feedback Loop**: Collect and store user feedback for continuous improvement

### Real-World Impact

- 🔒 **Security**: Azure Key Vault + Managed Identity eliminates secret exposure
- 🤖 **AI Power**: Gemini API integration with search grounding for better responses
- 💾 **Persistence**: MongoDB stores all chat sessions and user data
- 📊 **Analytics**: Track user behavior and feedback for insights
- ⚡ **Performance**: FastAPI provides high-performance async endpoints

---

## The Solution

### Architecture Overview

A well-structured FastAPI application:

1. **`main.py`** - Application entry point with route registration
2. **`dependencies.py`** - Shared dependencies (Key Vault, MongoDB, Gemini client)
3. **`api/`** - API route handlers organized by domain
4. **`shared/`** - Shared utilities and models
5. **`tests/`** - Comprehensive test suite (20 tests passing)

### Key Features

**Secure Secrets Management**:
- Azure Key Vault integration via `DefaultAzureCredential`
- No secrets in code or `.env` files
- Managed Identity for production, Azure CLI for local dev

**API Endpoints**:
- `POST /api/chat` - Proxy to Gemini API with search grounding
- `POST /api/users` - User subscription
- `PUT /api/users/{user_id}` - Update user preferences
- `GET /api/users/{user_id}/sessions` - Get user's chat sessions
- `GET /api/sessions/{session_id}/messages` - Get session messages
- `POST /api/sessions/{session_id}/messages` - Create message + get AI response
- `POST /api/feedback` - Record user feedback
- `POST /api/analytics` - Log analytics events

### Deployment Strategy

**Local Development**:
- Azure CLI authentication
- `.env` file with `KEY_VAULT_URI`
- Virtual environment with dependencies

**Production (Azure App Service)**:
- System-assigned Managed Identity
- Environment variable configuration
- CI/CD via GitHub Actions

---

## How It Works

### The Flow

```
┌─────────────┐
│ New Session │
└──────┬──────┘
       │
       ├─> Read claude.md (orientation)
       │
       ├─> Read .ai/INDEX.md (what's new?)
       │
       ├─> Read .ai/GUIDE.md (where to look?)
       │
       ├─> Find specific knowledge
       │
       ├─> Build feature/fix bug
       │
       ├─> Run /capture
       │
       └─> Knowledge base updated
```

### Knowledge Capture Process

1. **Build something** (feature, component, fix)
2. **Run `/capture`**
3. **AI analyzes** git diff and changed files
4. **AI generates** structured documentation
5. **INDEX.md updates** with recent changes
6. **Next session**: Knowledge is available

### Incremental Growth

- **Day 1**: Foundation with 0 documented features
- **Week 1**: 2-3 features documented, patterns emerging
- **Month 1**: 10+ features, comprehensive pattern library
- **Month 3**: Complete knowledge base, AI rarely searches codebase

---

## Core Design Principles

### 1. Discovery Over Search
AI knows where to look first, reducing time and token costs

### 2. Incremental Knowledge Capture
Every feature adds to the knowledge base automatically

### 3. Tool Agnostic
Works with Claude Code, Gemini, Cursor, or any AI assistant

### 4. Human Readable
All files are markdown + YAML, easy to read and edit

### 5. Structured Navigation
Hierarchical: claude.md → INDEX.md → GUIDE.md → specific knowledge → code

### 6. Low Overhead
Simple `/capture` command, no complex setup per task

### 7. Git-Friendly
Plain text files tracked in git, merges easily, diff-able

---

## Current Status

### Phase: Active Development

**What's Built**:
- ✅ FastAPI application with route registration
- ✅ Azure Key Vault integration (dependencies.py)
- ✅ MongoDB connection and models
- ✅ Gemini API integration
- ✅ Complete API endpoint suite (chat, users, sessions, feedback, analytics)
- ✅ Test suite with 20 passing tests
- ✅ Documentation (README.md, PRD in docs/)

**What's Next**:
1. Use `/capture` to document existing features
2. Continue expanding API functionality
3. Enhance test coverage
4. Add more analytics and monitoring

### Metrics (Current)

- **API Endpoints**: 8 routes implemented
- **Test Coverage**: 20 tests passing
- **Features documented**: 0 (ready to capture)
- **Components documented**: 0 (ready to capture)
- **Patterns documented**: 0 (ready to capture)

---

## Use Cases

### For This Project (Meta-System)

This project IS the knowledge management system itself. It's self-documenting - as we build features for the system, we use `/capture` to document them.

### For Future Projects

Once established, this system can be:

1. **Copied to new projects** as a template
2. **Customized** for specific tech stacks
3. **Extended** with project-specific patterns
4. **Shared** across teams for consistency

### For Different AI Tools

- **Claude Code**: Full integration with `/capture` command and slash commands
- **Gemini/Bard**: Read `claude.md`, follow same file structure
- **Cursor**: Point to knowledge files, same navigation
- **GitHub Copilot**: Can reference knowledge files in prompts
- **Human Developers**: All files human-readable, serves as documentation

---

## Success Criteria

### Quantitative

- **Discovery time**: < 30 seconds to find relevant information
- **Search reduction**: 70%+ reduction in full-repo searches
- **Knowledge coverage**: 100% of features documented
- **Index hit rate**: 60%+ of questions answered from INDEX.md

### Qualitative

- AI provides context-aware answers without clarifying questions
- New features automatically follow established patterns
- Code reviews reference project-specific standards
- Knowledge base grows organically with minimal effort
- New developers (human or AI) get up to speed in minutes

---

## Technology Stack

### Backend Framework

- **Python**: 3.9+
- **FastAPI**: High-performance async web framework
- **Uvicorn**: ASGI server for running FastAPI

### Database & Storage

- **MongoDB**: NoSQL database via pymongo
- Collections: users, sessions, messages, feedback, analytics

### AI Integration

- **Google Gemini API**: google-generativeai library
- Search grounding enabled for enhanced responses

### Security & Authentication

- **Azure Key Vault**: Centralized secrets management
- **Azure Identity**: DefaultAzureCredential for authentication
- **Managed Identity**: Production authentication (Azure App Service)
- **Azure CLI**: Local development authentication

### Development Tools

- **pytest**: Testing framework (20 tests passing)
- **python-dotenv**: Local environment configuration
- **Git**: Version control

### Deployment

- **Azure App Service**: Linux-based Python hosting
- **GitHub Actions**: CI/CD pipeline (potential)
- **Environment Variables**: KEY_VAULT_URI configuration

---

## Related Documentation

- [Architecture](./architecture.md) - How the system is structured
- [Decisions](./decisions/) - Major architectural decisions (empty for now)
- [INDEX.md](../INDEX.md) - Current state and recent changes
- [GUIDE.md](../GUIDE.md) - How to navigate the knowledge base
- [claude.md](../../claude.md) - AI entry point and orientation

---

## Philosophy

> "The best documentation is the one that's always up to date."

By capturing knowledge automatically as features are built, we eliminate the doc/code drift problem. Documentation is generated from reality (git changes) not aspirational intentions.

> "AI should know where to look, not search everything."

Structured navigation beats unstructured search. Like a well-organized library vs. a pile of books.

> "Start simple, grow organically."

Begin with minimal structure. Add complexity only when needed. Let the project guide its evolution.

---

**Last Updated**: 2025-11-08 (Foundation)
