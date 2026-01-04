"""Kubernetes package search tool with FTS and deterministic ranking."""
from typing import Dict, Any, List
from app.db import execute_query
from app.ranking import rank_k8s_packages
from app.config import get_settings

settings = get_settings()


def search_k8s_packages(
    query: str,
    top_k: int = None
) -> Dict[str, Any]:
    """
    Search Kubernetes/Bitnami packages using keyword and FTS.
    
    Uses PostgreSQL full-text search on name and description,
    then applies deterministic ranking.
    
    Args:
        query: Search query string
        top_k: Number of results to return
        
    Returns:
        Dict with results list and metadata
    """
    top_k = top_k or settings.k8s_top_k
    
    # Build FTS query using ts_rank for relevance
    search_query = """
        SELECT 
            package_id::text,
            name,
            normalized_name,
            description,
            version,
            app_version,
            category,
            official,
            cncf,
            deprecated,
            stars,
            license,
            repository_name,
            repository_official,
            keywords,
            stats_subscriptions as subscriptions
        FROM cloud.bitnami_packages
        WHERE 
            (
                search_tsv @@ plainto_tsquery('english', %s)
                OR LOWER(name) LIKE LOWER(%s)
                OR LOWER(description) LIKE LOWER(%s)
            )
            AND (deprecated IS NULL OR deprecated = false)
        ORDER BY 
            ts_rank(search_tsv, plainto_tsquery('english', %s)) DESC,
            stars DESC NULLS LAST,
            official DESC NULLS LAST
        LIMIT 50
    """
    
    query_like = f"%{query}%"
    params = (query, query_like, query_like, query)
    
    results = execute_query(search_query, params)
    
    # Apply deterministic ranking
    ranked_results = rank_k8s_packages(results, query)
    
    return {
        "results": ranked_results[:top_k],
        "metadata": {
            "total_found": len(ranked_results),
            "top_k": top_k,
            "query": query
        }
    }


def format_k8s_for_llm(results: List[Dict[str, Any]]) -> str:
    """
    Format K8s package results for LLM consumption.
    
    Args:
        results: List of K8s packages
        
    Returns:
        Formatted string for LLM
    """
    if not results:
        return "No Kubernetes packages found matching the query."
    
    lines = ["Found Kubernetes packages (Helm charts):"]
    for r in results:
        official_badge = " [OFFICIAL]" if r.get('official') else ""
        cncf_badge = " [CNCF]" if r.get('cncf') else ""
        stars_info = f" ⭐{r.get('stars', 0)}" if r.get('stars') else ""
        
        desc = r.get('description', '')
        if desc and len(desc) > 100:
            desc = desc[:97] + "..."
        
        lines.append(
            f"{r['rank']}. {r['name']}{official_badge}{cncf_badge}{stars_info} | "
            f"v{r.get('version', 'N/A')} | {desc}"
        )
    
    return "\n".join(lines)

