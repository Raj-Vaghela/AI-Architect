# Backend Integration Report

## Discovery Method
Inspected backend source code directly (`app/main.py` and `app/schemas.py`) to determine exact API endpoints and payloads.

## Discovered Backend Endpoints

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: Set via `NEXT_PUBLIC_BACKEND_URL` environment variable

### Chat Endpoints

#### 1. Start Conversation
- **Method**: `POST`
- **Path**: `/api/v1/chat/start`
- **Request**: No body required
- **Response**:
```json
{
  "conversation_id": "uuid-string",
  "message": "Conversation started. How can I help you deploy your workload?"
}
```

#### 2. Send Message
- **Method**: `POST`
- **Path**: `/api/v1/chat/message`
- **Request**:
```json
{
  "conversation_id": "uuid-string",
  "message": "user message text"
}
```
- **Response**:
```json
{
  "conversation_id": "uuid-string",
  "response": "assistant response text",
  "response_type": "clarification" | "deployment_plan" | "error",
  "deployment_plan": {
    "understanding": "...",
    "assumptions": ["..."],
    "gpu_recommendations": [...],
    "model_recommendations": [...],
    "kubernetes_stack": [...],
    "deployment_steps": [...],
    "cost_estimate": {...},
    "tradeoffs": [...]
  } // Optional, only when response_type is "deployment_plan"
}
```

#### 3. Get Conversation History
- **Method**: `GET`
- **Path**: `/api/v1/chat/{conversation_id}`
- **Request**: No body (conversation_id in URL)
- **Response**:
```json
{
  "conversation_id": "uuid-string",
  "messages": [
    {
      "id": "msg-uuid",
      "role": "user" | "assistant" | "system",
      "content": "message text",
      "created_at": "2025-12-29T03:00:00Z"
    }
  ]
}
```

## CORS Configuration
✅ **Backend already has CORS enabled** (`allow_origins=["*"]` in `main.py:68-74`)
- No proxy needed for development
- Direct browser fetch will work
- No backend modifications required

## Conversation Management Strategy

### Per-User Storage
Conversations are stored in `localStorage` with the following structure:

```typescript
// Key format: `s8_conversations:{user_id}`
interface StoredConversation {
  id: string;              // Backend conversation_id
  title: string;           // Auto-generated or user-provided
  userId: string;         // From Supabase auth
  createdAt: string;      // ISO timestamp
  lastUpdatedAt: string;  // ISO timestamp
}
```

### Workflow
1. User logs in → Load conversations from localStorage for their user_id
2. "New Chat" → Call POST `/api/v1/chat/start` → Store conversation in localStorage
3. Send message → Call POST `/api/v1/chat/message` → Update lastUpdatedAt
4. Switch conversation → Call GET `/api/v1/chat/{conversation_id}` → Load messages
5. Backend handles message persistence; frontend only stores conversation metadata

## Implementation Files

### New Files
1. `frontend/src/lib/config.ts` - Environment variable validation
2. `frontend/src/lib/backend.ts` - Backend API connector with typed methods
3. `frontend/src/lib/conversationStorage.ts` - LocalStorage manager for conversations
4. `frontend/src/hooks/useConversations.ts` - React hook for conversation management

### Modified Files
1. `frontend/src/app/chat/page.tsx` - Connect to real backend, implement multi-turn
2. `frontend/src/components/MessageBubble.tsx` - Render deployment_plan if present
3. `frontend/.env.local` - Add `NEXT_PUBLIC_BACKEND_URL=http://localhost:8000`

## Backend Modifications
**None required.** CORS is already configured for all origins.

## Error Handling
- Network errors: Show toast, allow retry
- 404 (conversation not found): Clear from localStorage, redirect to new chat
- 500 (backend error): Display error from `response` field, allow retry
- Timeout: 30s timeout on requests, show loading indicator

## Testing Checklist
- [ ] Login with Supabase Google Auth works
- [ ] New conversation creation works (POST /start)
- [ ] First message sends successfully (POST /message)
- [ ] Second message in same conversation works (multi-turn)
- [ ] Switching between conversations loads correct history
- [ ] Deployment plan renders when response_type is "deployment_plan"
- [ ] Error messages display correctly
- [ ] Conversation list persists across page reloads
