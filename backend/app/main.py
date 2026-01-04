"""FastAPI API server (DB-backed chat memory with per-user ownership)."""

from datetime import datetime
import logging
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.agents.unified_agent import run_agent
from app.auth import get_user_id, verify_conversation_access
from app.constants import TitleGeneration
from app.db import (
    add_message,
    conversation_belongs_to_user,
    conversation_exists,
    create_conversation,
    delete_conversation,
    get_conversation_messages,
    list_conversations_for_user,
    update_conversation_title,
)
from app.schemas import (
    ChatStartResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationHistoryResponse,
    ConversationListResponse,
    ConversationMessage,
    ConversationSummary,
    ComputeSearchRequest,
    HFSearchRequest,
    K8sSearchRequest,
    ToolSearchResponse,
)
from app.tools.compute_tool import search_compute_instances
from app.tools.hf_tool import search_hf_models
from app.tools.k8s_tool import search_k8s_packages


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(title="Stack8s Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _clean_for_llm(history: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Keep only (role, content) for LLM context."""
    return [{"role": m["role"], "content": m["content"]} for m in history]


def _generate_conversation_title(user_message: str, assistant_response: str) -> str:
    """
    Generate a concise, descriptive title for the conversation using AI.
    
    Args:
        user_message: The first user message
        assistant_response: The assistant's first response
        
    Returns:
        A short title (3-6 words) describing the conversation topic
    """
    from openai import OpenAI
    from app.config import get_settings
    
    try:
        client = OpenAI(api_key=get_settings().openai_api_key)
        
        prompt = f"""Based on this conversation, generate a very short, descriptive title (3-6 words max).

User: {user_message[:TitleGeneration.MAX_MESSAGE_PREVIEW]}
Assistant: {assistant_response[:TitleGeneration.MAX_MESSAGE_PREVIEW]}

Generate ONLY the title, nothing else. Make it concise and specific.
Examples:
- "Deploy LLaMA Model on GPU"
- "Kubernetes Setup for BERT"
- "Cost Analysis: Vision Model"
- "ResNet Deployment Configuration"

Title:"""
        
        response = client.chat.completions.create(
            model=TitleGeneration.MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=TitleGeneration.MAX_TOKENS,
            temperature=TitleGeneration.TEMPERATURE,
        )
        
        title = response.choices[0].message.content.strip()
        
        # Remove quotes that some LLMs add around generated titles
        title = title.strip('"').strip("'").strip()
        
        # Truncate for UI display (sidebar has limited width)
        if len(title) > TitleGeneration.MAX_TITLE_LENGTH:
            title = title[:TitleGeneration.TRUNCATE_AT] + TitleGeneration.ELLIPSIS
        
        return title if title else "New Conversation"
        
    except Exception as e:
        logger.warning(f"Failed to generate title: {e}")
        # Fallback: use truncated user message
        max_fallback_length = 40
        if len(user_message) > max_fallback_length:
            return user_message[:max_fallback_length] + TitleGeneration.ELLIPSIS
        return user_message


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0", "ts": datetime.utcnow().isoformat()}

@app.get("/")
async def root():
    return {"status": "ok", "service": "Stack8s Backend"}

@app.post("/api/v1/chat/start", response_model=ChatStartResponse)
async def start_chat(user_id: str = Depends(get_user_id)):
    """Start a new conversation for the logged-in user (stored in Postgres)."""
    try:
        conversation_id = create_conversation(user_id=user_id)
        greeting = "Hello! I'm your Stack8s Consultant. Tell me about the AI workload you want to deploy!"
        add_message(conversation_id, "assistant", greeting)
        return ChatStartResponse(conversation_id=conversation_id, message=greeting)
    except Exception as e:
        logger.exception("Failed to start chat")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/chat/message", response_model=ChatMessageResponse)
async def chat_message(request: ChatMessageRequest, user_id: str = Depends(get_user_id)):
    """
    Send a message in an existing conversation.
    
    Args:
        request: Message request with conversation_id and message text
        user_id: Authenticated user ID (verified via JWT)
        
    Returns:
        ChatMessageResponse with assistant's reply
        
    Raises:
        HTTPException: 404 if conversation not found, 403 if unauthorized
    """
    # Verify conversation access
    verify_conversation_access(request.conversation_id, user_id)
    
    logger.info(f"📨 [INCOMING] user={user_id} conv={request.conversation_id} msg={request.message[:120]}")

    try:
        # Get message count before adding new message
        history_before = get_conversation_messages(request.conversation_id)
        is_first_user_message = len([m for m in history_before if m["role"] == "user"]) == 0
        
        add_message(request.conversation_id, "user", request.message)
        history = get_conversation_messages(request.conversation_id)
        response_text = run_agent(_clean_for_llm(history))
        add_message(request.conversation_id, "assistant", response_text)
        
        # Generate title after first real exchange (not the greeting)
        if is_first_user_message:
            try:
                logger.info("🏷️  [TITLE] Generating conversation title...")
                title = _generate_conversation_title(request.message, response_text)
                update_conversation_title(request.conversation_id, title)
                logger.info(f"🏷️  [TITLE] Generated: {title}")
            except Exception as title_error:
                logger.warning(f"Failed to update title: {title_error}")

        return ChatMessageResponse(
            conversation_id=request.conversation_id,
            response=response_text,
            response_type="deployment_plan",
            deployment_plan=None
        )
    except Exception as e:
        logger.exception("Error processing message")
        error_text = f"I encountered an error processing your request: {str(e)}"
        try:
            add_message(request.conversation_id, "assistant", error_text)
        except Exception:
            pass
        return ChatMessageResponse(
            conversation_id=request.conversation_id,
            response=error_text,
            response_type="error",
            deployment_plan=None,
        )

@app.get("/api/v1/chat/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_history(conversation_id: str, user_id: str = Depends(get_user_id)):
    """
    Get full conversation history with all messages.
    
    Args:
        conversation_id: UUID of the conversation
        user_id: Authenticated user ID (from JWT token)
        
    Returns:
        ConversationHistoryResponse with all messages in chronological order
        
    Raises:
        HTTPException: 404 if conversation not found, 403 if user doesn't own it
    """
    # Verify conversation access
    verify_conversation_access(conversation_id, user_id)

    rows = get_conversation_messages(conversation_id)
    return ConversationHistoryResponse(
        conversation_id=conversation_id,
        messages=[
            ConversationMessage(
                id=r["id"],
                role=r["role"],
                content=r["content"],
                created_at=r["created_at"],
            )
            for r in rows
        ],
    )


@app.get("/api/v1/chat", response_model=ConversationListResponse)
async def list_my_conversations(user_id: str = Depends(get_user_id)):
    """List previous chats for this user (for 'show my chats on login')."""
    rows = list_conversations_for_user(user_id=user_id, limit=50)
    return ConversationListResponse(
        user_id=user_id,
        conversations=[
            ConversationSummary(
                id=r["id"],
                title=r.get("title"),
                created_at=r["created_at"],
                updated_at=r["updated_at"],
            )
            for r in rows
        ],
    )


@app.delete("/api/v1/chat/{conversation_id}")
async def delete_chat(conversation_id: str, user_id: str = Depends(get_user_id)):
    """
    Delete a conversation and all its messages.
    
    Args:
        conversation_id: UUID of the conversation to delete
        user_id: Authenticated user ID (from JWT token)
        
    Returns:
        Success response with conversation_id
        
    Raises:
        HTTPException: 404 if conversation not found, 403 if unauthorized, 500 if delete fails
    """
    # Verify conversation access
    verify_conversation_access(conversation_id, user_id)
    
    deleted = delete_conversation(conversation_id, user_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete conversation")
    
    return {"success": True, "conversation_id": conversation_id}


@app.post("/api/v1/tools/compute/search", response_model=ToolSearchResponse)
async def tool_compute_search(req: ComputeSearchRequest):
    result = search_compute_instances(
        gpu_needed=req.gpu_needed,
        min_vram_gb=req.min_vram_gb,
        gpu_model=req.gpu_model,
        max_price_monthly=req.max_price_monthly,
        provider=req.provider,
        region=req.region,
        min_vcpu=req.min_vcpu,
        min_ram_gb=req.min_ram_gb,
        top_k=req.top_k,
    )
    return ToolSearchResponse(results=result["results"], metadata=result["metadata"])


@app.post("/api/v1/tools/k8s/search", response_model=ToolSearchResponse)
async def tool_k8s_search(req: K8sSearchRequest):
    result = search_k8s_packages(query=req.query, top_k=req.top_k)
    return ToolSearchResponse(results=result["results"], metadata=result["metadata"])


@app.post("/api/v1/tools/hf/search", response_model=ToolSearchResponse)
async def tool_hf_search(req: HFSearchRequest):
    result = search_hf_models(
        query=req.query,
        pipeline_tag=req.pipeline_tag,
        license_filter=req.license_filter,
        top_k=req.top_k,
    )
    return ToolSearchResponse(results=result["results"], metadata=result["metadata"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
