# Stack8s API Reference

Complete HTTP API reference for the Stack8s backend.

**Base URL:** `http://localhost:8000` (development)

**Authentication:** All chat endpoints require Bearer token authentication using Supabase JWT.

---

## Table of Contents

- [Authentication](#authentication)
- [Health & Status](#health--status)
- [Chat Endpoints](#chat-endpoints)
- [Tool Search Endpoints](#tool-search-endpoints)
- [Error Responses](#error-responses)

---

## Authentication

### Bearer Token

All chat endpoints require a Supabase JWT access token in the Authorization header:

```http
Authorization: Bearer <supabase_access_token>
```

**Getting the Token:**
- Frontend: `await supabase.auth.getSession()` → `session.access_token`
- CLI scripts: Use `X-User-Id` header (development only)

**Token Validation:**
- Supports HS256 (legacy secret), RS256/ES256 (JWKS), and remote validation
- Tokens expire based on Supabase Auth configuration
- Invalid/expired tokens return `401 Unauthorized`

---

## Health & Status

### GET `/health`

Check if the API server is running.

**Authentication:** Not required

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "ts": "2025-12-31T10:30:00.000Z"
}
```

### GET `/`

Root endpoint.

**Authentication:** Not required

**Response:**
```json
{
  "status": "ok",
  "service": "Stack8s Backend"
}
```

---

## Chat Endpoints

### POST `/api/v1/chat/start`

Start a new conversation for the authenticated user.

**Authentication:** Required

**Request:**
```http
POST /api/v1/chat/start
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Hello! I'm your Stack8s Consultant. Tell me about the AI workload you want to deploy!"
}
```

**Errors:**
- `401` - Missing or invalid authentication token
- `500` - Server error creating conversation

---

### POST `/api/v1/chat/message`

Send a message in an existing conversation.

**Authentication:** Required

**Request:**
```http
POST /api/v1/chat/message
Authorization: Bearer <token>
Content-Type: application/json

{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "I want to deploy LLaMA 3.1 70B"
}
```

**Response:** `200 OK`
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "Great! For LLaMA 3.1 70B, you'll need substantial GPU resources...",
  "response_type": "deployment_plan",
  "deployment_plan": null
}
```

**Response Types:**
- `deployment_plan` - Full deployment plan with recommendations
- `clarification` - Agent needs more information
- `error` - Error occurred during processing

**Errors:**
- `401` - Missing or invalid authentication token
- `403` - Conversation doesn't belong to user
- `404` - Conversation not found
- `500` - Error processing message

**Notes:**
- AI-generated title is created after first user message
- Messages are persisted to database
- Conversation history included in agent context (last 10 messages)

---

### GET `/api/v1/chat/{conversation_id}`

Get full conversation history with all messages.

**Authentication:** Required

**Request:**
```http
GET /api/v1/chat/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "id": "msg-1",
      "role": "assistant",
      "content": "Hello! I'm your Stack8s Consultant...",
      "created_at": "2025-12-31T10:00:00.000Z"
    },
    {
      "id": "msg-2",
      "role": "user",
      "content": "I want to deploy LLaMA 3.1 70B",
      "created_at": "2025-12-31T10:01:00.000Z"
    },
    {
      "id": "msg-3",
      "role": "assistant",
      "content": "Great! For LLaMA 3.1 70B...",
      "created_at": "2025-12-31T10:01:15.000Z"
    }
  ]
}
```

**Message Roles:**
- `assistant` - Messages from Stack8s AI
- `user` - Messages from the user
- `system` - System messages (rare)

**Errors:**
- `401` - Missing or invalid authentication token
- `403` - Conversation doesn't belong to user
- `404` - Conversation not found

---

### GET `/api/v1/chat`

List all conversations for the authenticated user.

**Authentication:** Required

**Request:**
```http
GET /api/v1/chat
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "user_id": "abf6afe8-9085-4bf2-974c-1c9266884e7b",
  "conversations": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "LLaMA 3.1 Kubernetes Deployment",
      "created_at": "2025-12-31T10:00:00.000Z",
      "updated_at": "2025-12-31T10:15:00.000Z"
    },
    {
      "id": "660f9511-f39c-52e5-b827-557766551111",
      "title": "BERT GPU Requirements",
      "created_at": "2025-12-30T15:30:00.000Z",
      "updated_at": "2025-12-30T16:00:00.000Z"
    }
  ]
}
```

**Notes:**
- Conversations sorted by `updated_at` DESC (most recent first)
- Limited to 50 most recent conversations
- Titles are AI-generated after first exchange

**Errors:**
- `401` - Missing or invalid authentication token

---

### DELETE `/api/v1/chat/{conversation_id}`

Delete a conversation and all its messages.

**Authentication:** Required

**Request:**
```http
DELETE /api/v1/chat/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "success": true,
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Notes:**
- Cascade deletes all messages in the conversation
- Deletion is permanent and cannot be undone
- Only conversation owner can delete

**Errors:**
- `401` - Missing or invalid authentication token
- `403` - Conversation doesn't belong to user
- `404` - Conversation not found
- `500` - Failed to delete conversation

---

## Tool Search Endpoints

These endpoints allow direct access to the search tools (primarily for testing).

### POST `/api/v1/tools/compute/search`

Search for cloud compute instances.

**Authentication:** Not required (tool endpoint)

**Request:**
```http
POST /api/v1/tools/compute/search
Content-Type: application/json

{
  "gpu_needed": true,
  "min_vram_gb": 40,
  "gpu_model": "A100",
  "max_price_monthly": 1000,
  "top_k": 10
}
```

**Request Parameters:**
- `gpu_needed` (boolean, optional) - Whether GPU is required
- `min_vram_gb` (integer, optional) - Minimum VRAM in GB
- `gpu_model` (string, optional) - GPU model (A100, H100, T4, L4)
- `max_price_monthly` (number, optional) - Max monthly price in USD
- `provider` (string, optional) - Cloud provider (aws, gcp, azure)
- `region` (string, optional) - Preferred region
- `min_vcpu` (integer, optional) - Minimum vCPU cores
- `min_ram_gb` (number, optional) - Minimum RAM in GB
- `top_k` (integer, default: 10) - Number of results to return

**Response:** `200 OK`
```json
{
  "results": [
    {
      "provider": "gcp",
      "instance_name": "a2-highgpu-1g",
      "gpu_model": "A100",
      "gpu_count": 1,
      "vram_per_gpu_gb": 40,
      "total_vram_gb": 40,
      "vcpu": 12,
      "ram_gb": 85,
      "price_monthly": 872.40,
      "price_hourly": 1.18,
      "regions": ["us-central1", "europe-west4"]
    }
  ],
  "metadata": {
    "query_params": {...},
    "total_results": 5
  }
}
```

---

### POST `/api/v1/tools/k8s/search`

Search for Kubernetes/Helm packages.

**Authentication:** Not required (tool endpoint)

**Request:**
```http
POST /api/v1/tools/k8s/search
Content-Type: application/json

{
  "query": "mlflow",
  "top_k": 15
}
```

**Request Parameters:**
- `query` (string, required) - Search query (package name or description)
- `top_k` (integer, default: 15) - Number of results to return

**Response:** `200 OK`
```json
{
  "results": [
    {
      "name": "mlflow",
      "description": "Open source platform for the machine learning lifecycle",
      "version": "1.2.3",
      "category": "ml-tools",
      "official": true,
      "stars": 1250
    }
  ],
  "metadata": {
    "query": "mlflow",
    "total_results": 3
  }
}
```

---

### POST `/api/v1/tools/hf/search`

Search for HuggingFace models.

**Authentication:** Not required (tool endpoint)

**Request:**
```http
POST /api/v1/tools/hf/search
Content-Type: application/json

{
  "query": "llama 3",
  "pipeline_tag": "text-generation",
  "license_filter": ["apache-2.0", "mit"],
  "top_k": 5
}
```

**Request Parameters:**
- `query` (string, required) - Search query (model name or description)
- `pipeline_tag` (string, optional) - Pipeline tag filter (text-generation, image-to-text, etc.)
- `license_filter` (array of strings, optional) - Acceptable licenses
- `top_k` (integer, default: 5) - Number of results to return

**Response:** `200 OK`
```json
{
  "results": [
    {
      "model_id": "meta-llama/Llama-3-70B",
      "pipeline_tag": "text-generation",
      "license": "llama3",
      "downloads": 1500000,
      "likes": 25000,
      "relevance_score": 0.95
    }
  ],
  "metadata": {
    "query": "llama 3",
    "total_results": 12
  }
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

| Code | Meaning | When It Happens |
|------|---------|-----------------|
| `200` | OK | Request successful |
| `401` | Unauthorized | Missing or invalid authentication token |
| `403` | Forbidden | User doesn't have access to this resource |
| `404` | Not Found | Resource (conversation) doesn't exist |
| `500` | Internal Server Error | Unexpected server error |
| `503` | Service Unavailable | External service (Supabase Auth) unavailable |

### Error Examples

**401 Unauthorized:**
```json
{
  "detail": "Missing Authorization Bearer token (Supabase access_token)."
}
```

**403 Forbidden:**
```json
{
  "detail": "Conversation does not belong to this user"
}
```

**404 Not Found:**
```json
{
  "detail": "Conversation not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Failed to start chat"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. Future versions may add:
- Per-user rate limits
- Title generation rate limits
- API endpoint rate limits

---

## Versioning

Current API version: `v1`

All endpoints are prefixed with `/api/v1/`. Future versions will use `/api/v2/`, etc.

**Breaking changes** will result in a new version. Non-breaking changes may be added to current version.

---

## Development Tips

### Testing with cURL

**Start a conversation:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/start \
  -H "Authorization: Bearer YOUR_SUPABASE_TOKEN"
```

**Send a message:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Authorization: Bearer YOUR_SUPABASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "YOUR_CONV_ID", "message": "Hello!"}'
```

**List conversations:**
```bash
curl http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer YOUR_SUPABASE_TOKEN"
```

### Testing with Python

See `backend/scripts/test_auth_chat.py` for a complete example.

### Frontend Integration

See `frontend/src/lib/backend.ts` for TypeScript client implementation.

---

## Support

For issues or questions:
- Check error logs in terminal
- Review `CHATBOT_ARCHITECTURE.md` for system overview
- Check `SUPABASE_AUTH_SETUP.md` for auth configuration

---

**Last Updated:** December 31, 2025  
**API Version:** 1.0.0

