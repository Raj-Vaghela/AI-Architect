# Stack8s Backend Documentation

Complete documentation for the Stack8s backend system.

## Quick Links

- **[Setup Guide](setup/QUICKSTART.md)** - Get started quickly
- **[API Reference](api/API_REFERENCE.md)** - Complete HTTP API documentation
- **[Architecture Overview](architecture/CHATBOT_ARCHITECTURE.md)** - System design and components

---

## Documentation Structure

### 📚 Setup & Getting Started

Getting the backend up and running:

- **[Quickstart Guide](setup/QUICKSTART.md)** - Fast setup for development
- **[Supabase Auth Setup](setup/SUPABASE_AUTH_SETUP.md)** - Configure authentication
- **[Chat Persistence Setup](setup/QUICK_START_CHAT_PERSISTENCE.md)** - Enable persistent chat storage

### 🏗️ Architecture

Understanding the system design:

- **[Chatbot Architecture](architecture/CHATBOT_ARCHITECTURE.md)** - Complete system architecture
- **[Backend Build Report](architecture/backend_build_report.md)** - Build process and decisions
- **[PRD Alignment Report](architecture/PRD_ALIGNMENT_REPORT.md)** - Product requirements alignment

### ✨ Features

Feature-specific documentation:

- **[AI Title Generation](features/AI_TITLE_GENERATION.md)** - Auto-generated conversation titles
- **[Chat Persistence](features/CHAT_PERSISTENCE_IMPLEMENTATION.md)** - Multi-user chat storage
- **[Chat Deletion](features/CHAT_DELETE_FEATURE.md)** - Delete conversations feature

### 🔌 API Reference

HTTP API documentation:

- **[Complete API Reference](api/API_REFERENCE.md)** - All endpoints, authentication, errors

### 📖 General Documentation

Other important documents:

- **[How to Chat](HOW_TO_CHAT.md)** - Using the chat interface
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** - What's been implemented
- **[Implementation Complete](IMPLEMENTATION_COMPLETE.md)** - Final implementation status
- **[Improvements Made](IMPROVEMENTS_MADE.md)** - Recent improvements
- **[Status](STATUS.md)** - Current project status

---

## For Developers

### First Time Setup

1. Read [Quickstart Guide](setup/QUICKSTART.md)
2. Configure [Supabase Auth](setup/SUPABASE_AUTH_SETUP.md)
3. Review [Architecture Overview](architecture/CHATBOT_ARCHITECTURE.md)
4. Check [API Reference](api/API_REFERENCE.md)

### Adding Features

1. Review existing [feature documentation](features/)
2. Update [Architecture](architecture/CHATBOT_ARCHITECTURE.md) if needed
3. Add endpoint to [API Reference](api/API_REFERENCE.md)
4. Create feature documentation in `features/`

### Testing

Test scripts are in `backend/scripts/`:
- `test_auth_chat.py` - Test chat persistence and auth
- `test_delete_chat.py` - Test deletion functionality
- `test_title_generation.py` - Test AI title generation
- `test_api.py` - General API testing

### Code Organization

```
backend/
├── app/
│   ├── agents/          # AI agent logic
│   ├── tools/           # Search tools (compute, k8s, hf)
│   ├── auth.py          # JWT authentication
│   ├── config.py        # Configuration management
│   ├── constants.py     # Application constants
│   ├── db.py            # Database operations
│   ├── main.py          # FastAPI application
│   ├── ranking.py       # Result ranking logic
│   └── schemas.py       # Pydantic models
├── docs/                # Documentation (you are here)
├── migrations/          # Database migrations
└── scripts/             # Utility and test scripts
```

---

## Documentation Guidelines

When adding documentation:

1. **Place in correct folder:**
   - Setup guides → `setup/`
   - Feature docs → `features/`
   - Architecture → `architecture/`
   - API docs → `api/`

2. **Use clear titles** that explain what the doc covers

3. **Include examples** where appropriate

4. **Update this README** with links to new docs

5. **Use markdown formatting** for readability

---

## Need Help?

- Check [Quickstart Guide](setup/QUICKSTART.md) for common issues
- Review [API Reference](api/API_REFERENCE.md) for endpoint details
- See [Architecture](architecture/CHATBOT_ARCHITECTURE.md) for system overview

---

**Last Updated:** December 31, 2025


