"""Local cluster tool (stub implementation)."""
from typing import Dict, Any


def check_local_cluster() -> Dict[str, Any]:
    """
    Check if local Kubernetes cluster is available.
    
    This is a stub implementation that always returns "not connected".
    In a real implementation, this would check kubectl connectivity,
    available resources, etc.
    
    Returns:
        Dict with connection status and message
    """
    return {
        "connected": False,
        "message": "Local cluster not connected",
        "details": {
            "cluster_available": False,
            "reason": "No local cluster configured"
        }
    }


def format_local_for_llm(result: Dict[str, Any]) -> str:
    """
    Format local cluster result for LLM consumption.
    
    Args:
        result: Local cluster check result
        
    Returns:
        Formatted string for LLM
    """
    if result.get('connected'):
        return f"Local cluster available: {result.get('message', '')}"
    else:
        return f"Local cluster not available: {result.get('message', 'Not connected')}"

