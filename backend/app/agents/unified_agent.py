"""
Unified Agent: The complete Stack8s assistant.
Role: Friendly consultant with technical expertise.
Capabilities:
- Conversational and helpful
- Autonomous tool usage
- Technical accuracy
- Direct user interaction
"""
import json
import logging
from typing import List, Dict, Any
from openai import OpenAI
from app.config import get_settings
from app.constants import AgentConfig
from app.tools.compute_tool import search_compute_instances
from app.tools.hf_tool import search_hf_models
from app.tools.k8s_tool import search_k8s_packages
from app.tools.local_tool import check_local_cluster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent")

# Tool definitions
ALL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_compute_instances",
            "description": "Search for cloud compute instances (CPU or GPU). Use for: traditional ML (CPUs fine), web APIs, databases, lightweight inference (CPUs), deep learning training (GPUs), LLM serving (GPUs). For GPU workloads: LLM training needs ~2GB VRAM per billion params (fp16). Leave gpu_needed empty to see all options.",
            "parameters": {
                "type": "object",
                "properties": {
                    "gpu_needed": {
                        "type": "boolean", 
                        "description": "True = only GPU instances, False = only CPU instances, omit/null = show both CPU and GPU options. Use True for: deep learning, LLMs, vision models. Use False for: traditional ML, web services, databases. Omit when unsure."
                    },
                    "min_vram_gb": {"type": "integer", "description": "Minimum GPU VRAM in GB (only relevant if gpu_needed=true)"},
                    "gpu_model": {"type": "string", "description": "GPU model filter: A100, H100, T4, L4 (only if gpu_needed=true)"},
                    "max_price_monthly": {"type": "number", "description": "Maximum monthly price in USD"},
                    "provider": {"type": "string", "description": "Cloud provider: aws, gcp, azure, etc."},
                    "min_vcpu": {"type": "integer", "description": "Minimum vCPU cores (useful for both CPU and GPU instances)"},
                    "min_ram_gb": {"type": "number", "description": "Minimum system RAM in GB"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_hf_models",
            "description": "Search HuggingFace for AI models. Check license compatibility for commercial use.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query (e.g., 'llama 3', 'stable diffusion')"},
                    "pipeline_tag": {"type": "string", "description": "Pipeline tag (text-generation, image-to-text)"},
                    "license_filter": {"type": "array", "items": {"type": "string"}, "description": "Acceptable licenses"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_k8s_packages",
            "description": "Search for Helm charts and Kubernetes packages. Prefer official/bitnami charts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Software name (mlflow, kibana, ingress-nginx)"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_local_cluster",
            "description": "Check if local Kubernetes cluster is available",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

def get_system_prompt() -> str:
    return """You're a knowledgeable AI infrastructure consultant helping users deploy their AI workloads on Stack8s.

Have a natural conversation - you're talking to someone who needs help, not filling out a form. Listen to what they need, ask questions when it helps, and give them practical advice.

What you help with:
- Finding the right compute (CPUs for traditional ML/APIs, GPUs for deep learning)
- Recommending AI models from HuggingFace that fit their use case
- Suggesting Kubernetes components and infrastructure tools
- Designing their deployment architecture

How to be helpful:
- When you need to know more, just ask naturally - like "What's your budget looking like?" or "Are you training from scratch or fine-tuning?"
- Use your tools to get real data - prices, GPU specs, model info. Never make up numbers.
- Share what you find and explain why it matters for their specific situation
- If there are multiple good options, talk through the tradeoffs
- Keep your responses conversational - no rigid sections or templates unless it genuinely helps

Quick technical notes for yourself:
- NOT everything needs a GPU! Traditional ML (scikit-learn, XGBoost), APIs, databases, and lightweight inference can run on CPUs
- When to use CPUs: web services, traditional ML, small model inference, data processing, feature engineering
- When to use GPUs: deep learning training, LLM serving, computer vision, large model inference
- LLM memory: roughly 2GB per billion params in fp16 (so 70B ≈ 140GB VRAM)
- Always check model licenses if they're doing commercial work
- Multi-GPU training needs good interconnect (NVLink/InfiniBand)
- Cost-effective GPU options: T4 (inference), L4 (inference), A100 (training), H100 (large-scale training)
- Quantization (int8/int4) can cut memory needs significantly

Tools you have:
- search_compute_instances: find cloud GPUs and pricing
- search_hf_models: search HuggingFace models
- search_k8s_packages: find Kubernetes tools
- check_local_cluster: check if they have local compute

Just talk to them like you're a helpful colleague who knows this stuff well. Be friendly, be clear, and help them figure out what they actually need. 🚀"""


def json_serializer(obj):
    """Handle datetime and Decimal serialization"""
    from datetime import datetime, date
    from decimal import Decimal
    
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    
    raise TypeError(f"Type {type(obj)} not serializable")

def run_tool(tool_call, tool_map) -> Dict[str, Any]:
    """Execute a tool call"""
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    
    logger.info(f"\n{'='*80}")
    logger.info(f"🛠️  [TOOL CALL] {name}")
    logger.info(f"{'='*80}")
    logger.info(f"📥 Arguments:")
    for key, value in args.items():
        logger.info(f"   • {key}: {value}")
    
    if name in tool_map:
        try:
            result = tool_map[name](**args)
            
            # Log detailed output
            logger.info(f"\n📤 Tool Output:")
            
            if isinstance(result, dict):
                # Log results count
                if 'results' in result:
                    logger.info(f"   ✓ Found {len(result['results'])} results")
                    
                    # Log first few results in detail
                    for i, item in enumerate(result['results'][:3], 1):
                        logger.info(f"\n   Result #{i}:")
                        if isinstance(item, dict):
                            for k, v in list(item.items())[:5]:  # First 5 fields
                                if isinstance(v, (list, dict)):
                                    logger.info(f"      {k}: {str(v)[:50]}...")
                                else:
                                    logger.info(f"      {k}: {v}")
                        else:
                            logger.info(f"      {str(item)[:100]}")
                    
                    if len(result['results']) > 3:
                        logger.info(f"   ... and {len(result['results']) - 3} more results")
                
                # Log metadata
                if 'metadata' in result:
                    logger.info(f"\n   Metadata: {result['metadata']}")
            else:
                # For non-dict results, show preview
                result_str = str(result)
                if len(result_str) > 500:
                    logger.info(f"   {result_str[:500]}...")
                    logger.info(f"   ... ({len(result_str)} total chars)")
                else:
                    logger.info(f"   {result_str}")
            
            logger.info(f"\n✅ Tool execution completed successfully")
            logger.info(f"{'='*80}\n")
            
            return result
            
        except Exception as e:
            logger.error(f"\n❌ Tool execution failed: {str(e)}")
            logger.info(f"{'='*80}\n")
            return {"error": f"Tool {name} failed: {str(e)}"}
    else:
        logger.error(f"❌ Tool not found: {name}")
        logger.info(f"{'='*80}\n")
        return {"error": f"Tool {name} not found"}

def run_agent(conversation_history: List[Dict[str, str]]) -> str:
    """
    Run the unified agent with ReAct loop.
    Returns: User-friendly response (Markdown).
    """
    client = OpenAI(api_key=get_settings().openai_api_key)
    model = get_settings().openai_chat_model
    
    tool_map = {
        "search_compute_instances": search_compute_instances,
        "search_hf_models": search_hf_models,
        "search_k8s_packages": search_k8s_packages,
        "check_local_cluster": check_local_cluster
    }
    
    messages = [{"role": "system", "content": get_system_prompt()}]
    messages.extend(conversation_history[-AgentConfig.MAX_HISTORY_MESSAGES:])
    
    logger.info("💬 [AGENT] Processing request...")
    
    # ReAct Loop
    for iteration in range(AgentConfig.MAX_ITERATIONS):
        logger.info(f"🔄 [ITERATION {iteration + 1}/{AgentConfig.MAX_ITERATIONS}]")
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=ALL_TOOLS,
                tool_choice="auto",
                temperature=AgentConfig.TEMPERATURE
            )
            
            message = response.choices[0].message
            
            # If no tool calls, return the response
            if not message.tool_calls:
                logger.info(f"✅ [AGENT] Response ready ({len(message.content)} chars)")
                return message.content
            
            # Log how many tools the agent wants to call
            logger.info(f"   🤔 Agent wants to call {len(message.tool_calls)} tool(s)")
            
            # Add assistant message to history
            messages.append(message.model_dump(exclude_unset=True))
            
            # Execute tool calls
            for tool_call in message.tool_calls:
                result = run_tool(tool_call, tool_map)
                
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_call.function.name,
                    "content": json.dumps(result, default=json_serializer)
                })
                
        except Exception as e:
            logger.error(f"❌ [AGENT] Error: {e}")
            return f"I encountered an error: {str(e)}. Please try again."
    
    logger.warning(f"⚠️  [AGENT] Hit max iterations ({AgentConfig.MAX_ITERATIONS})")
    return "I'm having trouble completing this request. Could you rephrase or simplify it?"
