# 🚀 Setup Instructions - Do These 3 Things

## ✅ Step 1: Get JWT Secret (2 minutes)

### Where to get it:
1. **Click this link:** https://supabase.com/dashboard/project/qzamfduqlcdwktobwarl/settings/api
2. **Login to Supabase** (if not already logged in)
3. **Scroll down** to find the section labeled **"JWT Settings"**
4. **Find "JWT Secret"** - it looks like this:

```
JWT Secret
super-secret-jwt-token-with-at-least-32-characters-long
[Copy button]
```

5. **Click the copy button** or select and copy the entire secret

---

## ✅ Step 2: Add JWT Secret to Backend (1 minute)

### File to edit:
**Location:** `E:\Stack8s\backend\.env.local`

### What to paste:
**Add these 2 lines at the end of the file:**

```env
SUPABASE_JWT_SECRET=paste-your-jwt-secret-here
SUPABASE_PROJECT_URL=https://qzamfduqlcdwktobwarl.supabase.co
```

**Replace `paste-your-jwt-secret-here` with the actual JWT secret you copied in Step 1.**

### Example:
If your JWT secret is `abc123xyz789`, your file should have:

```env
SUPABASE_JWT_SECRET=abc123xyz789
SUPABASE_PROJECT_URL=https://qzamfduqlcdwktobwarl.supabase.co
```

---

## ✅ Step 3: Frontend Fixed! (Already Done)

✅ **I've already updated the frontend code for you!**

The file `frontend/src/lib/backend.ts` now sends JWT tokens automatically.

---

## 🧪 Test It Out

### Start Backend:
```powershell
cd E:\Stack8s\backend
.\venv\Scripts\Activate.ps1
python -m app.main
```

### Start Frontend (in a new terminal):
```powershell
cd E:\Stack8s\frontend
npm run dev
```

### Test:
1. Open browser: http://localhost:3000
2. Login with Google
3. Start chatting
4. Your chats are now saved! 🎉

---

## 🎯 What This Does

### Before:
- ❌ Chats were stored in local memory (lost when you close browser)
- ❌ Couldn't access chats from other devices

### After:
- ✅ Chats saved to database permanently
- ✅ Access chats from any device
- ✅ Each user sees only their own chats
- ✅ Secure authentication with Google login

---

## ❓ Troubleshooting

### Error: "Not authenticated. Please log in again."
**Fix:** Login with Google again. Your session might have expired.

### Error: "Missing Authorization Bearer token"
**Fix:** Make sure you added the JWT secret to `.env.local` correctly.

### Error: "Invalid or expired Supabase token"
**Fix:** Your JWT secret might be wrong. Double-check it in the Supabase dashboard.

### Backend won't start
**Fix:** Make sure `.env.local` has all required variables (check `env.example` for reference).

---

## 📋 Quick Checklist

- [ ] Got JWT secret from Supabase dashboard
- [ ] Added `SUPABASE_JWT_SECRET` to `backend/.env.local`
- [ ] Added `SUPABASE_PROJECT_URL` to `backend/.env.local`
- [ ] Started backend server
- [ ] Started frontend server
- [ ] Logged in with Google
- [ ] Tested creating a chat
- [ ] Verified chat persists after refresh

---

## 🎉 That's It!

Your chat persistence is now fully working! All chats will be saved to the database and accessible from any device.


