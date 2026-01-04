# Stack8s - AI Architect

AI-powered cloud workload deployment planning system with multi-agent architecture.

## 🏗️ Project Structure

This is a full-stack application consisting of:

- **Backend**: FastAPI-based multi-agent system for deployment planning
- **Frontend**: Next.js web application
- **Dashboard**: Simple HTML/JS dashboard

## 📚 Documentation

### Backend
See [backend/README.md](backend/README.md) for complete backend documentation including:
- API Reference
- Architecture Overview
- Setup Instructions
- Testing Guide

### Frontend
See [frontend/README.md](frontend/README.md) for frontend setup and development.

## 🚀 Quick Start

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp env.example .env.local
# Edit .env.local with your configuration
```

4. Run database migrations (see backend README for details)

5. Start the server:
```bash
python -m app.main
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables:
```bash
cp env.example .env.local
# Edit .env.local with your configuration
```

4. Start the development server:
```bash
npm run dev
```

## 🎯 Features

- ✅ Multi-agent architecture (Requirements Agent + Architect Agent)
- ✅ Tool-driven retrieval (Compute, K8s, HuggingFace, Local)
- ✅ Multi-turn chat with persistent memory
- ✅ Per-user chat persistence with Supabase Auth
- ✅ Secure user isolation
- ✅ Cross-device chat access
- ✅ RAG-based model search using pgvector
- ✅ Deterministic retrieval with fixed ranking

## 🛠️ Tech Stack

### Backend
- FastAPI
- PostgreSQL (Supabase) with pgvector
- OpenAI API
- Pydantic

### Frontend
- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- Supabase Auth

## 📖 License

See LICENSE file for details.

## 🤝 Contributing

See project documentation for contribution guidelines.

