# Supabase Auth Setup for Multi-User Chat Persistence

## Overview

Your Stack8s backend now supports **per-user chat persistence** using Supabase Auth! This means:
- ✅ Each user's chats are stored in the database
- ✅ Users can access their chats from any device
- ✅ Chats persist across sessions
- ✅ Secure authentication via Google login

## Architecture

```
Frontend (Google Login)
    ↓
Supabase Auth (JWT Token)
    ↓
Backend API (Verifies JWT)
    ↓
PostgreSQL Database (Stores chats per user_id)
```

## Setup Instructions

### 1. Get Your Supabase JWT Secret

1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project: `qzamfduqlcdwktobwarl`
3. Navigate to: **Project Settings** → **API**
4. Find the **JWT Secret** section
5. Copy the value (it's a long string like `super-secret-jwt-token-with-at-least-32-characters-long`)

### 2. Configure Environment Variables

Create a `.env.local` file in the `backend/` directory:

```bash
# Copy the example file
cp env.example .env.local
```

Then edit `.env.local` and add your JWT secret:

```env
# Database (you already have this)
SUPABASE_DB_URL=postgresql://postgres:YOUR_PASSWORD@YOUR_HOST:YOUR_PORT/postgres

# Supabase Auth (ADD THESE)
SUPABASE_JWT_SECRET=your-actual-jwt-secret-from-dashboard
SUPABASE_PROJECT_URL=https://qzamfduqlcdwktobwarl.supabase.co

# OpenAI (you already have this)
OPENAI_API_KEY=sk-...
OPENAI_CHAT_MODEL=gpt-4o-mini
```

### 3. Verify Database Schema

The database schema is already set up! The migrations have been applied:
- ✅ `chat.conversations` table with `user_id` column
- ✅ `chat.messages` table
- ✅ Indexes for fast queries
- ✅ Foreign key constraints

You can verify by running:

```sql
SELECT * FROM chat.conversations LIMIT 5;
```

### 4. Test the Setup

#### Option A: Using the Chat Script (Development)

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python scripts\chat.py
```

**Note:** The chat script uses `X-User-Id` header for development testing. To test with real Supabase Auth, you need to:

1. Get a real JWT token from your frontend after Google login
2. Use it in the `Authorization: Bearer <token>` header

#### Option B: Using the Frontend (Production)

1. Start the backend:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m app.main
```

2. Start your frontend (wherever it is)
3. Login with Google
4. Start a chat
5. The backend will automatically:
   - Extract the user ID from the JWT token
   - Store the conversation with that user ID
   - Return only that user's conversations

## How It Works

### Frontend Flow

```javascript
// 1. User logs in with Google via Supabase Auth
const { data: { session } } = await supabase.auth.signInWithOAuth({
  provider: 'google'
})

// 2. Get the access token
const accessToken = session.access_token

// 3. Send requests with the token
fetch('http://localhost:8000/api/v1/chat/start', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
})
```

### Backend Flow

```python
# 1. FastAPI receives request with Authorization header
# 2. get_user_id() dependency extracts and verifies JWT
# 3. Extracts user_id from JWT 'sub' claim
# 4. All database operations use this user_id
```

### Database Structure

```sql
-- Conversations table
chat.conversations
  - id: UUID (primary key)
  - user_id: TEXT (Supabase Auth user UUID)
  - title: TEXT
  - created_at: TIMESTAMP
  - updated_at: TIMESTAMP

-- Messages table
chat.messages
  - id: UUID (primary key)
  - conversation_id: UUID (foreign key)
  - role: TEXT ('user' or 'assistant')
  - content: TEXT
  - created_at: TIMESTAMP
```

## API Endpoints

### 1. Start a New Chat

```http
POST /api/v1/chat/start
Authorization: Bearer <supabase_jwt_token>
```

Response:
```json
{
  "conversation_id": "uuid-here",
  "message": "Hello! I'm your Stack8s Consultant..."
}
```

### 2. Send a Message

```http
POST /api/v1/chat/message
Authorization: Bearer <supabase_jwt_token>
Content-Type: application/json

{
  "conversation_id": "uuid-here",
  "message": "I need to deploy a vision model"
}
```

### 3. Get Chat History

```http
GET /api/v1/chat/{conversation_id}
Authorization: Bearer <supabase_jwt_token>
```

### 4. List All User's Chats

```http
GET /api/v1/chat
Authorization: Bearer <supabase_jwt_token>
```

Response:
```json
{
  "user_id": "auth-user-uuid",
  "conversations": [
    {
      "id": "conv-uuid-1",
      "title": "GPU Selection for Lung Cancer Detection",
      "created_at": "2025-12-24T23:02:53.823091",
      "updated_at": "2025-12-24T23:12:24.10246"
    }
  ]
}
```

## Security Features

### 1. JWT Verification
- All tokens are verified using the Supabase JWT secret
- Expired tokens are rejected
- Invalid tokens return 401 Unauthorized

### 2. User Isolation
- Users can only access their own conversations
- Attempting to access another user's conversation returns 403 Forbidden
- All queries filter by `user_id`

### 3. Development Fallback
- In development mode, you can use `X-User-Id` header for testing
- This is disabled in production (`ENVIRONMENT=production`)

## Testing Checklist

- [ ] Backend starts without errors
- [ ] JWT secret is configured in `.env.local`
- [ ] Frontend can login with Google
- [ ] Frontend gets JWT token from Supabase
- [ ] Backend accepts requests with JWT token
- [ ] New conversations are created with correct user_id
- [ ] Messages are stored in the database
- [ ] User can see their chat history
- [ ] User can access chats from different devices
- [ ] User cannot access other users' chats

## Troubleshooting

### Error: "Missing Authorization Bearer token"
- **Cause:** Frontend is not sending the JWT token
- **Fix:** Ensure `Authorization: Bearer <token>` header is included in all requests

### Error: "Invalid or expired Supabase token"
- **Cause:** JWT token has expired or is invalid
- **Fix:** Refresh the token using Supabase Auth's `refreshSession()` method

### Error: "Supabase auth not configured"
- **Cause:** `SUPABASE_JWT_SECRET` is not set in `.env.local`
- **Fix:** Add the JWT secret from your Supabase dashboard

### Error: "Conversation does not belong to this user"
- **Cause:** Trying to access another user's conversation
- **Fix:** This is expected behavior - users can only access their own chats

### Database Connection Issues
- **Cause:** `SUPABASE_DB_URL` is incorrect or database is unreachable
- **Fix:** Verify the connection string in Supabase Dashboard > Database Settings

## Migration from Local Storage

If you previously had chats stored in local memory:

1. **Old chats are lost** - Local memory is not persistent
2. **New chats are saved** - All new chats will be saved to the database
3. **No migration needed** - Just start using the new system

## Next Steps

1. ✅ Configure `.env.local` with your JWT secret
2. ✅ Test with a real Google login from your frontend
3. ✅ Verify chats are saved in the database
4. ✅ Test accessing chats from a different device
5. 🎉 Enjoy persistent, multi-user chat!

## Need Help?

If you encounter any issues:
1. Check the backend logs for error messages
2. Verify your JWT token is valid (decode it at jwt.io)
3. Ensure your `.env.local` has all required variables
4. Test the `/health` endpoint to verify the server is running

## Code References

- **Auth Logic:** `backend/app/auth.py`
- **Database Functions:** `backend/app/db.py`
- **API Endpoints:** `backend/app/main.py`
- **Configuration:** `backend/app/config.py`
- **Migrations:** `backend/migrations/`

