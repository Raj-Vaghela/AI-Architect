"""Pydantic models for request/response validation."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


# ============================================================================
# Chat API Models
# ============================================================================

class ChatStartResponse(BaseModel):
    """Response for starting a new chat conversation."""
    conversation_id: str
    message: str = "Conversation started. How can I help you deploy your workload?"


class ChatMessageRequest(BaseModel):
    """Request to send a message in a conversation."""
    conversation_id: str
    message: str


class ChatMessageResponse(BaseModel):
    """Response from the assistant in a conversation."""
    conversation_id: str
    response: str
    response_type: Literal["clarification", "deployment_plan", "error"]
    deployment_plan: Optional["DeploymentPlan"] = None


class ConversationMessage(BaseModel):
    """A single message in conversation history."""
    id: str
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime


class ConversationHistoryResponse(BaseModel):
    """Full conversation history."""
    conversation_id: str
    messages: List[ConversationMessage]


class ConversationSummary(BaseModel):
    """Summary info for listing a user's conversations."""
    id: str
    title: str | None = None
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    """List of conversations for a user."""
    user_id: str
    conversations: List[ConversationSummary]


# ============================================================================
# Agent Models
# ============================================================================

class WorkloadSpec(BaseModel):
    """Structured workload specification extracted by Requirements Agent."""
    model_config = ConfigDict(protected_namespaces=())
    
    task_type: Optional[Literal["training", "inference", "fine-tuning"]] = None
    domain: Optional[str] = None  # e.g., "computer vision", "NLP", "LLM"
    budget_monthly: Optional[float] = None
    budget_constraint: Optional[str] = None  # e.g., "strict", "flexible"
    region_preference: Optional[List[str]] = None
    provider_preference: Optional[List[str]] = None
    gpu_needed: Optional[bool] = None
    min_vram_gb: Optional[int] = None
    gpu_model_preference: Optional[List[str]] = None
    model_needs: Optional[str] = None  # e.g., "stable diffusion", "llama 70B"
    kubernetes_needs: Optional[List[str]] = None  # e.g., ["mlflow", "prometheus"]
    scale_requirements: Optional[str] = None
    
    # Metadata
    confidence_level: Optional[str] = "low"  # low, medium, high
    missing_fields: Optional[List[str]] = None


class ClarificationQuestion(BaseModel):
    """A single clarification question."""
    question: str
    field: str  # Which WorkloadSpec field this clarifies
    why_needed: str


class ClarificationResponse(BaseModel):
    """Response when agent needs clarification."""
    questions: List[ClarificationQuestion]
    current_understanding: WorkloadSpec


class GPURecommendation(BaseModel):
    """A GPU instance recommendation."""
    rank: int
    provider: str
    instance_name: str
    gpu_model: str
    gpu_count: int
    vram_per_gpu_gb: int
    total_vram_gb: int
    vcpu: int
    ram_gb: float
    price_monthly: float
    price_hourly: float
    regions: List[str]
    reasoning: str
    

class ModelRecommendation(BaseModel):
    """A HuggingFace model recommendation."""
    model_config = ConfigDict(protected_namespaces=())
    
    rank: int
    model_id: str
    pipeline_tag: Optional[str]
    license: Optional[str]
    downloads: int
    likes: int
    relevance_score: float
    reasoning: str


class K8sPackage(BaseModel):
    """A Kubernetes/Bitnami package recommendation."""
    name: str
    description: Optional[str]
    version: Optional[str]
    category: Optional[str]
    official: bool
    stars: Optional[int]
    reasoning: str


class DeploymentPlan(BaseModel):
    """Complete deployment plan from Architect Agent."""
    model_config = ConfigDict(protected_namespaces=())
    
    understanding: str  # Summary of what we're deploying
    assumptions: List[str]  # What we assumed when incomplete info
    
    # Recommendations
    gpu_recommendations: List[GPURecommendation]
    model_recommendations: List[ModelRecommendation]
    kubernetes_stack: List[K8sPackage]
    
    # Deployment guidance
    deployment_steps: List[str]
    cost_estimate: Dict[str, Any]  # breakdown by component
    tradeoffs: List[str]  # key tradeoffs and alternatives
    
    # Metadata
    local_cluster_available: bool = False


# ============================================================================
# Tool Debug API Models
# ============================================================================

class ComputeSearchRequest(BaseModel):
    """Request for compute instance search."""
    gpu_needed: Optional[bool] = None
    min_vram_gb: Optional[int] = None
    gpu_model: Optional[str] = None
    max_price_monthly: Optional[float] = None
    provider: Optional[str] = None
    region: Optional[str] = None
    min_vcpu: Optional[int] = None
    min_ram_gb: Optional[float] = None
    top_k: int = 10


class K8sSearchRequest(BaseModel):
    """Request for Kubernetes package search."""
    query: str
    top_k: int = 15


class HFSearchRequest(BaseModel):
    """Request for HuggingFace model search."""
    query: str
    pipeline_tag: Optional[str] = None
    license_filter: Optional[List[str]] = None
    top_k: int = 5


class ToolSearchResponse(BaseModel):
    """Generic tool search response."""
    results: List[Dict[str, Any]]
    metadata: Dict[str, Any]


# Update forward references
ChatMessageResponse.model_rebuild()

