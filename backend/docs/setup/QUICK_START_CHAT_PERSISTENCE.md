# Quick Start: Chat Persistence with Supabase Auth

## TL;DR - What You Need to Do

### 1. Get JWT Secret (2 minutes)
1. Go to: https://supabase.com/dashboard/project/qzamfduqlcdwktobwarl/settings/api
2. Copy the **JWT Secret** (under "JWT Settings")

### 2. Create `.env.local` (1 minute)
```bash
cd backend
cp env.example .env.local
```

Edit `.env.local` and add:
```env
SUPABASE_JWT_SECRET=paste-your-jwt-secret-here
SUPABASE_PROJECT_URL=https://qzamfduqlcdwktobwarl.supabase.co
```

### 3. Update Frontend (5 minutes)
Make sure your frontend sends the JWT token:

```javascript
// After Google login
const { data: { session } } = await supabase.auth.signInWithOAuth({
  provider: 'google'
})

// Send token with every request
fetch('http://localhost:8000/api/v1/chat/start', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${session.access_token}`,
    'Content-Type': 'application/json'
  }
})
```

### 4. Test It! (2 minutes)
```powershell
# Start backend
cd backend
.\venv\Scripts\Activate.ps1
python -m app.main

# In another terminal, run test
python scripts\test_auth_chat.py
```

## That's It! 🎉

Your chats are now:
- ✅ Saved to database
- ✅ Accessible from any device
- ✅ Isolated per user
- ✅ Persistent forever

## What Changed?

**Nothing breaks!** The chatbot works exactly the same, but now:
- Chats are saved to PostgreSQL instead of local memory
- Each user sees only their own chats
- Users can access chats from any device

## Files to Reference

- **Setup Guide:** `SUPABASE_AUTH_SETUP.md` (detailed instructions)
- **Implementation Details:** `CHAT_PERSISTENCE_IMPLEMENTATION.md` (technical details)
- **Environment Template:** `env.example` (copy this to `.env.local`)
- **Test Suite:** `scripts/test_auth_chat.py` (verify everything works)

## Need Help?

1. Check backend logs for errors
2. Verify JWT token at https://jwt.io
3. Ensure `.env.local` has all required variables
4. Test `/health` endpoint: `curl http://localhost:8000/health`

## Questions?

- **Where are chats stored?** PostgreSQL database (`chat.conversations` and `chat.messages` tables)
- **How does auth work?** JWT tokens from Supabase Auth (Google login)
- **Can users see other users' chats?** No, each user only sees their own
- **What if token expires?** Frontend should refresh using `supabase.auth.refreshSession()`
- **Does this affect chatbot functionality?** No, chatbot works exactly the same!

