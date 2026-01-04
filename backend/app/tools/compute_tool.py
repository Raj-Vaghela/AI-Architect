"""Compute instance retrieval tool with SQL filtering and deterministic ranking."""
from typing import Dict, Any, List, Optional
from app.db import execute_query
from app.ranking import rank_compute_instances
from app.config import get_settings

settings = get_settings()


def search_compute_instances(
    gpu_needed: Optional[bool] = None,
    min_vram_gb: Optional[int] = None,
    gpu_model: Optional[str] = None,
    max_price_monthly: Optional[float] = None,
    provider: Optional[str] = None,
    region: Optional[str] = None,
    min_vcpu: Optional[int] = None,
    min_ram_gb: Optional[float] = None,
    top_k: Optional[int] = None
) -> Dict[str, Any]:
    """
    Search compute instances with structured SQL filters.
    
    Args:
        gpu_needed: True = must have GPU, False = prefer no GPU, None = any
        min_vram_gb: Minimum GPU VRAM in GB
        gpu_model: GPU model name (partial match)
        max_price_monthly: Maximum monthly price
        provider: Provider name filter
        region: Region filter (checks if region in JSONB array)
        min_vcpu: Minimum vCPU cores
        min_ram_gb: Minimum RAM in GB
        top_k: Number of results to return
        
    Returns:
        Dict with results list and metadata
    """
    top_k = top_k or settings.compute_top_k
    
    # Build WHERE clauses
    where_clauses = []
    params = []
    
    # GPU filtering
    if gpu_needed is True:
        where_clauses.append("gpu_count > 0")
    elif gpu_needed is False:
        where_clauses.append("(gpu_count = 0 OR gpu_count IS NULL)")
    
    if min_vram_gb is not None:
        where_clauses.append("gpu_memory_gb >= %s")
        params.append(min_vram_gb)
    
    if gpu_model is not None:
        where_clauses.append("LOWER(gpu_model) LIKE LOWER(%s)")
        params.append(f"%{gpu_model}%")
    
    # Price filtering
    if max_price_monthly is not None:
        where_clauses.append("price_monthly <= %s")
        params.append(max_price_monthly)
    
    # Provider filtering
    if provider is not None:
        where_clauses.append("LOWER(provider) = LOWER(%s)")
        params.append(provider)
    
    # Region filtering (JSONB array contains check)
    if region is not None:
        where_clauses.append("regions @> %s::jsonb")
        params.append(f'["{region}"]')
    
    # Resource filtering
    if min_vcpu is not None:
        where_clauses.append("cpu_threads >= %s")
        params.append(min_vcpu)
    
    if min_ram_gb is not None:
        where_clauses.append("memory_gb >= %s")
        params.append(min_ram_gb)
    
    # Ensure availability
    where_clauses.append("(available = true OR available IS NULL)")
    
    # Build query
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    query = f"""
        SELECT 
            id::text,
            provider::text,
            name::text,
            instance_type::text,
            COALESCE(cpu_threads, 0)::integer as vcpu,
            COALESCE(memory_gb, 0)::numeric as ram_gb,
            COALESCE(gpu_count, 0)::integer as gpu_count,
            gpu_model::text,
            COALESCE(gpu_memory_gb, 0)::integer as vram_gb,
            COALESCE(price_monthly, 0)::numeric as price_monthly,
            COALESCE(price_hourly, 0)::numeric as price_hourly,
            regions,
            description::text
        FROM cloud.instances
        WHERE {where_sql}
        LIMIT 100
    """
    
    # Execute query
    results = execute_query(query, tuple(params) if params else None)
    
    # Apply deterministic ranking
    filters_used = {
        'gpu_needed': gpu_needed,
        'min_vram_gb': min_vram_gb,
        'gpu_model': gpu_model,
        'max_price_monthly': max_price_monthly,
        'provider': provider,
        'region': region,
        'min_vcpu': min_vcpu,
        'min_ram_gb': min_ram_gb
    }
    
    ranked_results = rank_compute_instances(results, filters_used)
    
    # Return top_k
    return {
        "results": ranked_results[:top_k],
        "metadata": {
            "total_found": len(ranked_results),
            "top_k": top_k,
            "filters_applied": {k: v for k, v in filters_used.items() if v is not None}
        }
    }


def format_compute_for_llm(results: List[Dict[str, Any]]) -> str:
    """
    Format compute results for LLM consumption.
    
    Args:
        results: List of compute instances
        
    Returns:
        Formatted string for LLM
    """
    if not results:
        return "No compute instances found matching the criteria."
    
    lines = ["Found compute instances (ranked by best fit):"]
    for r in results:
        gpu_info = ""
        if r.get('gpu_count'):
            gpu_info = f"{r['gpu_count']}x {r.get('gpu_model', 'GPU')} ({r.get('vram_gb', 0)}GB VRAM each)"
        else:
            gpu_info = "No GPU"
        
        lines.append(
            f"{r['rank']}. {r['provider']} - {r['name']} | "
            f"{gpu_info} | "
            f"{r.get('vcpu', 0)} vCPU, {r.get('ram_gb', 0):.1f}GB RAM | "
            f"${r.get('price_monthly', 0):.2f}/mo"
        )
    
    return "\n".join(lines)

