# 💬 How to Chat with Stack8s AI Architect

There are **4 easy ways** to chat with your AI Architect!

---

## Prerequisites

**Make sure your server is running:**

```powershell
# Terminal 1 - Start the server
cd E:\Stack8s\backend
.\venv\Scripts\Activate.ps1
python -m app.main
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started server process
INFO:     Application startup complete.
```

Keep this terminal running!

---

## Option 1: Web Browser Chat (Most Beautiful!) 🎨⭐

**Best for:** Visual, user-friendly experience

1. Make sure server is running (see above)
2. Open `backend/scripts/chat.html` in your browser:
   - Double-click the file, OR
   - Right-click → Open with → Chrome/Edge/Firefox

**Features:**
- ✨ Beautiful gradient UI
- 💬 Real-time chat interface
- 📋 Deployment plan summaries
- 🎯 Shows connection status
- 📱 Responsive design

**Example prompts to try:**
```
I need to deploy Llama 70B for inference

Help me train a computer vision model with a $3000 budget

Set up Stable Diffusion XL for image generation

I need GPUs for fine-tuning a language model
```

---

## Option 2: Interactive Python Script (Best for CLI) 💻⭐

**Best for:** Terminal lovers, quick testing

```powershell
# Open a NEW terminal (keep server running in Terminal 1)
cd E:\Stack8s\backend
.\venv\Scripts\Activate.ps1
$env:PYTHONIOENCODING='utf-8'
python scripts\chat.py
```

**Features:**
- 💬 Interactive command-line chat
- 📝 Full conversation history
- 🔄 Start new conversations with `new`
- 📜 View history with `history`
- 🚪 Exit with `quit` or `exit`

**Screenshot:**
```
================================================================================
  Stack8s AI Architect - Interactive Chat
================================================================================

Starting new conversation...
✓ Conversation started (ID: 198e1149...)

Type your messages below. Commands:
  - 'exit' or 'quit' to end chat
  - 'new' to start a new conversation
  - 'history' to see all messages

================================================================================

You: I need to deploy Llama 70B for inference

Thinking...

AI Architect [clarification]:
================================================================================
I need a bit more information to help you best:

1. What is your monthly budget for this deployment?
2. Do you have any specific GPU model preferences or requirements?
3. What regions do you prefer for this deployment?
================================================================================

You: _
```

---

## Option 3: Swagger UI (Best for API Testing) 🔧

**Best for:** Developers, API testing, seeing all endpoints

1. Make sure server is running
2. Open browser: http://localhost:8000/docs

**Steps:**
1. Click **"POST /api/v1/chat/start"**
2. Click **"Try it out"** → **"Execute"**
3. Copy the `conversation_id` from response
4. Click **"POST /api/v1/chat/message"**
5. Click **"Try it out"**
6. Paste your `conversation_id`
7. Type your message
8. Click **"Execute"**
9. See the AI's response!

**Features:**
- 📚 See all API endpoints
- 🧪 Test any endpoint
- 📄 API documentation
- 🔍 See request/response formats

---

## Option 4: PowerShell Script Demo 📜

**Best for:** Quick demo, automated testing

```powershell
cd E:\Stack8s\backend
.\scripts\chat_example.ps1
```

**What it does:**
1. Starts a conversation
2. Sends a test message
3. Displays the response
4. Shows conversation history

**Example output:**
```
================================
Stack8s AI Architect - Chat Demo
================================

Step 1: Starting conversation...
✓ Conversation ID: 198e1149-8a0c-41b6-931b-b208a6a0b5c6

Step 2: Sending message...

AI Response Type: clarification

--- AI Response ---
I need a bit more information to help you best:

1. What is your monthly budget for this deployment?
2. Do you have any specific GPU model preferences?
-------------------

Step 3: Fetching conversation history...
✓ Total messages: 2
```

---

## Quick Comparison

| Method | Best For | Difficulty | Visual |
|--------|----------|-----------|--------|
| **Web Browser** | Everyone | ⭐ Easiest | ✅ Beautiful |
| **Python Script** | CLI users | ⭐⭐ Easy | 📝 Text |
| **Swagger UI** | Developers | ⭐⭐ Easy | ✅ Good |
| **PowerShell** | Quick demo | ⭐⭐⭐ Medium | 📝 Text |

---

## Example Conversations

### Example 1: LLM Inference
```
You: I need to deploy Llama 70B for inference
AI: [Asks clarifying questions about budget, region, provider]

You: Budget is $5000/month, prefer AWS
AI: [Generates deployment plan with GPU recommendations, 
     model info, K8s stack, cost breakdown]
```

### Example 2: Computer Vision
```
You: Help me train a computer vision model for object detection

AI: [Asks about budget, GPU requirements, dataset size]

You: Budget $3000/month, need 2 GPUs with 24GB VRAM each

AI: [Generates deployment plan]:
  ✓ GPU: runpod RTX A5000 (2x 24GB) - $584/mo
  ✓ Models: facebook/detr-resnet-50, etc.
  ✓ K8s: MLflow, Kubeflow, Prometheus, Grafana
  ✓ Steps: 5 deployment steps
  ✓ Cost: $634/month breakdown
```

### Example 3: Stable Diffusion
```
You: Set up Stable Diffusion XL for image generation

AI: [Asks about budget, provider, scale requirements]

You: Budget $2000/month, need production-ready setup

AI: [Generates deployment plan]:
  ✓ GPU: L40S or A40 instances
  ✓ Models: Stable Diffusion XL variants
  ✓ K8s: vLLM/Triton for serving, Redis, NGINX
  ✓ Architecture for production inference
```

---

## Troubleshooting

### "Server not running" error

**Solution:**
```powershell
cd E:\Stack8s\backend
.\venv\Scripts\Activate.ps1
python -m app.main
```

### Web browser says "Cannot connect"

**Solution:**
- Check server is running at http://localhost:8000
- Try opening http://localhost:8000/health in browser
- If that works, refresh the chat page

### Python script encoding errors

**Solution:**
```powershell
$env:PYTHONIOENCODING='utf-8'
python scripts\chat.py
```

### PowerShell script won't run

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\chat_example.ps1
```

---

## Tips for Best Results

### 1. Be Specific
❌ "I need GPUs"
✅ "I need to deploy Llama 70B for inference with a budget of $3000/month"

### 2. Provide Context
✅ "I want to train a computer vision model for object detection. 
    I have a dataset of 100K images and need at least 24GB VRAM per GPU."

### 3. Mention Constraints
✅ "Budget is $2000/month, prefer AWS, need HIPAA compliance"

### 4. Ask Follow-ups
The AI maintains conversation context, so you can:
```
You: I need to deploy an LLM
AI: [Asks questions]
You: Budget is $5000/month
AI: [More questions]
You: Prefer GCP, need multi-region
AI: [Generates plan]
You: What if I reduce budget to $3000?
AI: [Adjusts recommendations]
```

---

## What the AI Can Help With

✅ **GPU Selection**
- Find best GPU instances across providers
- Compare prices and performance
- Get cost estimates

✅ **Model Recommendations**
- Search 30,403 HuggingFace models
- Get license information
- Match models to your task

✅ **Kubernetes Stack**
- Recommend ML frameworks
- Suggest observability tools
- Design complete infrastructure

✅ **Deployment Plans**
- Step-by-step deployment
- Cost breakdowns
- Architecture decisions
- Tradeoff analysis

---

## Advanced Usage

### Save Conversation for Later

```powershell
# Get conversation history
curl http://localhost:8000/api/v1/chat/YOUR_CONVERSATION_ID > my_conversation.json
```

### Use Different Models

Edit `backend/.env.local`:
```env
# Use better model for higher quality
OPENAI_CHAT_MODEL=gpt-4o  # Instead of gpt-4o-mini
```

### Debug Mode

Check server logs in Terminal 1 to see:
- What tools are being called
- What data is being retrieved
- How decisions are made

---

## Quick Start (TL;DR)

**Fastest way to start chatting:**

```powershell
# Terminal 1
cd E:\Stack8s\backend
.\venv\Scripts\Activate.ps1
python -m app.main

# Terminal 2
cd E:\Stack8s\backend
.\venv\Scripts\Activate.ps1
$env:PYTHONIOENCODING='utf-8'
python scripts\chat.py
```

**Or just double-click:**
`backend/scripts/chat.html`

---

**Happy Chatting! 🚀**

Need help? Check:
- `README.md` - Full documentation
- `QUICKSTART.md` - Setup guide
- `docs/PRD_ALIGNMENT_REPORT.md` - Feature details

