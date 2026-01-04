# Stack8s Backend API

Multi-agent FastAPI backend for AI-powered cloud workload deployment planning.

## 📚 Documentation

**Complete documentation is in the [docs/](docs/) folder:**

- **[Quick Start](docs/setup/QUICKSTART.md)** - Get up and running fast
- **[API Reference](docs/api/API_REFERENCE.md)** - Complete HTTP API documentation
- **[Architecture](docs/architecture/CHATBOT_ARCHITECTURE.md)** - System design overview
- **[Features](docs/features/)** - Feature-specific documentation
- **[Setup Guides](docs/setup/)** - Detailed setup instructions

**See [docs/README.md](docs/README.md) for the complete documentation index.**

## Architecture

This backend implements a 2-agent architecture with tool-driven retrieval:

1. **Requirements Agent**: Extracts structured WorkloadSpec from user messages or asks clarifying questions
2. **Architect Agent**: Uses tools to retrieve grounded information and builds deployment plans

### Tools

- **Compute Tool**: Searches cloud GPU/CPU instances with SQL filtering and deterministic ranking
- **K8s Tool**: Searches Kubernetes/Bitnami packages with FTS and keyword matching
- **HuggingFace Tool**: RAG-based model search using pgvector embeddings with reranking
- **Local Tool**: Stub for local cluster checking (always returns "not connected")

### Features

- ✅ Multi-turn chat with persistent memory (PostgreSQL)
- ✅ **Per-user chat persistence with Supabase Auth** (Google login)
- ✅ Secure user isolation - users can only access their own chats
- ✅ Cross-device chat access - chats available from any device
- ✅ Deterministic retrieval with fixed ranking weights
- ✅ RAG over HuggingFace model cards using pgvector
- ✅ Structured WorkloadSpec extraction
- ✅ Comprehensive DeploymentPlan generation
- ✅ Debug endpoints for testing tools independently

## Setup

### Prerequisites

- Python 3.10+
- PostgreSQL with pgvector extension (Supabase)
- OpenAI API key

### Installation

1. Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

2. Configure environment variables:

Create a `.env.local` file in the `backend/` directory:

```bash
# Copy the example file
cp env.example .env.local
```

Then edit `.env.local` with your values:

```env
# Database
SUPABASE_DB_URL=postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/postgres

# Supabase Auth (REQUIRED for multi-user chat persistence)
# Get JWT Secret from: Supabase Dashboard > Project Settings > API > JWT Secret
SUPABASE_JWT_SECRET=your-jwt-secret-here
SUPABASE_PROJECT_URL=https://[PROJECT_REF].supabase.co

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBED_MODEL=text-embedding-3-small

# HuggingFace RAG Configuration
HF_EMBEDDING_MODEL_NAME=text-embedding-3-small
HF_CHUNKER_VERSION=hf_chunker_v1

# API Configuration
API_PORT=8000
API_HOST=0.0.0.0

# Environment
ENVIRONMENT=development
```

**📖 For detailed setup instructions, see:** [docs/setup/QUICK_START_CHAT_PERSISTENCE.md](docs/setup/QUICK_START_CHAT_PERSISTENCE.md)

3. Run database migrations:

```bash
# Connect to your Supabase database and run:
psql $SUPABASE_DB_URL -f migrations/001_create_chat_schema.sql
```

Or use Supabase MCP to apply the migration:

```bash
# Read the migration file and apply via MCP
```

### Running the Server

Start the FastAPI server:

```bash
cd backend
python -m app.main
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

## API Endpoints

### Chat Endpoints

#### Start Conversation
```bash
POST /api/v1/chat/start
```

Creates a new conversation and returns `conversation_id`.

**Response:**
```json
{
  "conversation_id": "uuid",
  "message": "Conversation started. How can I help you deploy your workload?"
}
```

#### Send Message
```bash
POST /api/v1/chat/message
```

**Request:**
```json
{
  "conversation_id": "uuid",
  "message": "I need to deploy Llama 70B for inference"
}
```

**Response:**
```json
{
  "conversation_id": "uuid",
  "response": "string (markdown formatted)",
  "response_type": "clarification | deployment_plan | error",
  "deployment_plan": { ... } // Only if response_type is deployment_plan
}
```

#### Get Conversation History
```bash
GET /api/v1/chat/{conversation_id}
```

Returns all messages in the conversation.

### Tool Debug Endpoints

#### Compute Search
```bash
POST /api/v1/tools/compute/search
```

**Request:**
```json
{
  "gpu_needed": true,
  "min_vram_gb": 40,
  "max_price_monthly": 5000,
  "provider": "aws",
  "region": "us-east-1",
  "min_vcpu": 16,
  "min_ram_gb": 64,
  "top_k": 10
}
```

#### K8s Search
```bash
POST /api/v1/tools/k8s/search
```

**Request:**
```json
{
  "query": "mlflow",
  "top_k": 15
}
```

#### HuggingFace Search
```bash
POST /api/v1/tools/hf/search
```

**Request:**
```json
{
  "query": "stable diffusion image generation",
  "pipeline_tag": "text-to-image",
  "license_filter": ["apache-2.0", "mit"],
  "top_k": 5
}
```

## Testing

Run the test suite:

```bash
cd backend
python scripts/test_api.py
```

This will:
1. Test health check
2. Test all tool debug endpoints
3. Run 5 complete chat conversation scenarios
4. Validate responses

**Test Cases:**
1. LLM Inference (Llama 70B)
2. Computer Vision Training with budget constraints
3. Stable Diffusion XL setup
4. Fine-tuning with MLflow tracking
5. Minimal input (clarification flow)

## Database Schema

### Chat Schema

Created by `migrations/001_create_chat_schema.sql`

**Tables:**

- `chat.conversations`: Stores conversation metadata
  - `id` (UUID, PK)
  - `created_at`, `updated_at` (timestamps)
  - `title` (text, nullable)

- `chat.messages`: Stores individual messages
  - `id` (UUID, PK)
  - `conversation_id` (UUID, FK)
  - `role` (text: 'user' | 'assistant' | 'system')
  - `content` (text)
  - `created_at` (timestamp)

### Existing Schemas Used

- `cloud.instances`: GPU/CPU instance catalog with pricing, specs, regions
- `cloud.bitnami_packages`: Kubernetes Helm charts with FTS
- `hf.card_chunks`: Embedded HuggingFace model card chunks (pgvector)
- `hf.models`: HuggingFace model metadata (downloads, likes, license)
- `hf.model_to_card`: Mapping between models and card hashes

## Retrieval Logic

### Compute Tool (SQL Filtering)

**Filters:**
- GPU presence, VRAM, model
- Price constraints
- Provider, region
- vCPU, RAM minimums

**Ranking (deterministic):**
1. Price ascending
2. VRAM descending
3. GPU count descending
4. Provider alphabetical
5. Name alphabetical

### K8s Tool (FTS + Keyword)

**Search:**
- PostgreSQL full-text search on `search_tsv` column
- ILIKE keyword matching on name/description

**Ranking:**
1. Exact name match
2. Name starts with query
3. Query in name
4. Query in description
5. Stars descending
6. Official packages first
7. Name alphabetical

### HuggingFace Tool (RAG)

**Process:**
1. Embed query with OpenAI `text-embedding-3-small`
2. Vector search on `hf.card_chunks` (cosine similarity)
3. Aggregate chunk scores by `card_hash`
4. Map `card_hash` → models via `hf.model_to_card`
5. Join `hf.models` for metadata
6. Rerank by combined score: `0.6 * relevance + 0.4 * popularity`
7. Apply license/pipeline_tag filters
8. Return top 5

**Popularity:** `log(downloads + 1) + log(likes + 1)`, normalized

## Agent Behavior

### Requirements Agent

**Goal:** Extract WorkloadSpec or ask clarifying questions

**Process:**
1. Analyze conversation history
2. Extract structured fields (task_type, domain, gpu_needed, budget, etc.)
3. If confidence is "low" or critical fields missing → ask 1-3 clarifying questions
4. If confidence is "medium" or "high" → return WorkloadSpec

**Critical Fields:**
- `task_type`
- `domain`
- `gpu_needed`

### Architect Agent

**Goal:** Build comprehensive deployment plan using tools

**Process:**
1. Check local cluster (stub)
2. Search compute instances (based on WorkloadSpec)
3. Search HuggingFace models (if `model_needs` specified)
4. Search K8s packages (based on `kubernetes_needs` or defaults)
5. Synthesize with LLM into structured DeploymentPlan

**Output:** DeploymentPlan with:
- Understanding & assumptions
- Top 3 GPU recommendations (ranked)
- Top 5 model recommendations (ranked)
- Kubernetes stack (relevant charts)
- Deployment steps (ordered)
- Cost estimate (breakdown)
- Tradeoffs

## Configuration

All configuration is via environment variables (see `.env.local.template`).

**Key Settings:**
- `OPENAI_CHAT_MODEL`: LLM for agents (default: `gpt-4o-mini`)
- `OPENAI_EMBED_MODEL`: Embedding model for RAG (default: `text-embedding-3-small`)
- `HF_EMBEDDING_MODEL_NAME`: Must match the model used to create embeddings in DB
- `HF_CHUNKER_VERSION`: Must match chunker version in DB
- `*_TOP_K`: Fixed top_k for deterministic retrieval

## Development

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + routes
│   ├── config.py            # Settings management
│   ├── db.py                # Database helpers
│   ├── schemas.py           # Pydantic models
│   ├── ranking.py           # Deterministic ranking logic
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── requirements_agent.py
│   │   └── architect_agent.py
│   └── tools/
│       ├── __init__.py
│       ├── compute_tool.py
│       ├── k8s_tool.py
│       ├── hf_tool.py
│       └── local_tool.py
├── migrations/
│   └── 001_create_chat_schema.sql
├── scripts/
│   └── test_api.py
├── docs/
│   └── backend_build_report.md
├── requirements.txt
├── .env.local.template
└── README.md
```

### Adding New Tools

1. Create tool file in `app/tools/`
2. Implement search function with deterministic ranking
3. Add format function for LLM consumption
4. Add debug endpoint in `app/main.py`
5. Integrate into `architect_agent.py`

### Logging

Structured logging to stdout. Configure log level via:

```python
logging.basicConfig(level=logging.INFO)  # or DEBUG, WARNING, ERROR
```

## Deployment

### Production Considerations

1. **Database Connection Pooling**: Consider using `psycopg_pool` for connection pooling
2. **CORS**: Update `allow_origins` in `app/main.py` to restrict to your frontend domain
3. **Rate Limiting**: Add rate limiting middleware for production
4. **API Keys**: Use secrets management (not environment files)
5. **Monitoring**: Add APM (Application Performance Monitoring)
6. **Caching**: Consider caching tool results with Redis

### Environment Variables for Production

```env
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000
```

## Troubleshooting

### Database Connection Issues

```bash
# Test connection
psql $SUPABASE_DB_URL -c "SELECT version();"

# Check if chat schema exists
psql $SUPABASE_DB_URL -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'chat';"
```

### OpenAI API Issues

```bash
# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### HuggingFace RAG Not Working

1. Check embedding model name matches DB:
   ```sql
   SELECT DISTINCT embedding_model_name FROM hf.card_chunks;
   ```

2. Check chunker version matches DB:
   ```sql
   SELECT DISTINCT chunker_version FROM hf.card_chunks;
   ```

3. Verify embeddings exist:
   ```sql
   SELECT COUNT(*) FROM hf.card_chunks WHERE embedding IS NOT NULL;
   ```

## License

See project LICENSE file.

## Support

For issues and questions, refer to the project documentation or open an issue in the repository.

