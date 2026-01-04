# Stack8s Backend - Quick Start Guide

Get the backend running in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- PostgreSQL with pgvector (Supabase)
- OpenAI API key

## Step 1: Setup Environment

### Windows (PowerShell)
```powershell
cd backend
.\setup.ps1
```

### Linux/Mac (Bash)
```bash
cd backend
chmod +x setup.sh
./setup.sh
```

### Manual Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Configure Environment Variables

Copy the example environment file:
```bash
cp .env.local.example .env.local
```

Edit `.env.local` with your credentials:
```env
SUPABASE_DB_URL=postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/postgres
OPENAI_API_KEY=sk-your-key-here
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBED_MODEL=text-embedding-3-small
```

## Step 3: Database Migration (Already Applied! ✅)

The chat schema has been created automatically. To verify:

```bash
# Check tables exist
psql $SUPABASE_DB_URL -c "SELECT * FROM chat.conversations LIMIT 1;"
```

If you need to reapply manually:
```bash
psql $SUPABASE_DB_URL -f migrations/001_create_chat_schema.sql
```

## Step 4: Start the Server

```bash
python -m app.main
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 5: Test the API

### Option A: Run Full Test Suite
```bash
# In a new terminal
python scripts/test_api.py
```

### Option B: Manual Testing

**1. Health Check:**
```bash
curl http://localhost:8000/health
```

**2. Start a Conversation:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/start
```

**3. Send a Message:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "YOUR_CONVERSATION_ID",
    "message": "I need to deploy Llama 70B for inference"
  }'
```

**4. Test Tool Endpoints:**

Compute Search:
```bash
curl -X POST http://localhost:8000/api/v1/tools/compute/search \
  -H "Content-Type: application/json" \
  -d '{
    "gpu_needed": true,
    "min_vram_gb": 40,
    "max_price_monthly": 5000,
    "top_k": 5
  }'
```

K8s Search:
```bash
curl -X POST http://localhost:8000/api/v1/tools/k8s/search \
  -H "Content-Type: application/json" \
  -d '{"query": "mlflow", "top_k": 5}'
```

HuggingFace Search:
```bash
curl -X POST http://localhost:8000/api/v1/tools/hf/search \
  -H "Content-Type: application/json" \
  -d '{"query": "stable diffusion image generation", "top_k": 5}'
```

## Step 6: View API Documentation

Open in browser:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Troubleshooting

### Database Connection Error
```
psycopg.OperationalError: connection failed
```
**Solution:** Check `SUPABASE_DB_URL` in `.env.local`

### OpenAI API Error
```
openai.AuthenticationError: Invalid API key
```
**Solution:** Check `OPENAI_API_KEY` in `.env.local`

### Import Errors
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution:** Activate virtual environment and reinstall:
```bash
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Chat Schema Not Found
```
psycopg.errors.UndefinedTable: relation "chat.conversations" does not exist
```
**Solution:** Apply migration:
```bash
psql $SUPABASE_DB_URL -f migrations/001_create_chat_schema.sql
```

### HuggingFace Search Returns Empty
```json
{"results": [], "metadata": {...}}
```
**Solution:** Verify embeddings exist:
```bash
psql $SUPABASE_DB_URL -c "SELECT COUNT(*) FROM hf.card_chunks WHERE embedding IS NOT NULL;"
```

## Next Steps

1. ✅ Backend is running
2. ✅ Tests pass
3. 🎯 **Build the frontend** (Next.js)
4. 🚀 **Deploy to production**

## Development Tips

### Hot Reload
```bash
uvicorn app.main:app --reload
```

### Debug Mode
Set in `.env.local`:
```env
ENVIRONMENT=development
```

### View Logs
Server logs are printed to stdout. Redirect to file:
```bash
python -m app.main > server.log 2>&1
```

### Test Individual Endpoints
Use the Swagger UI at http://localhost:8000/docs for interactive testing.

## Production Deployment

See `README.md` for production deployment considerations:
- Connection pooling
- CORS configuration
- Rate limiting
- Secrets management
- Monitoring

---

**Need Help?** Check `README.md` or `docs/backend_build_report.md` for detailed documentation.

