"""Deterministic ranking logic for retrieval results."""
from typing import List, Dict, Any, Optional


def rank_compute_instances(
    instances: List[Dict[str, Any]],
    filters: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Rank compute instances deterministically based on constraints.
    
    Ranking criteria (in order):
    1. Meets all hard constraints (gpu, vram, price, vcpu, ram)
    2. Price ascending (cheaper first)
    3. VRAM descending (more VRAM preferred if equal price)
    4. GPU count descending
    5. Provider name ascending (alphabetical for tie-breaking)
    6. Instance name ascending (alphabetical for final tie-breaking)
    
    Args:
        instances: List of instance dictionaries from DB
        filters: Filter criteria used in query
        
    Returns:
        Sorted list of instances with rank field added
    """
    # Add constraint satisfaction score
    for inst in instances:
        inst['_meets_constraints'] = True  # Already filtered by SQL
        inst['_sort_key'] = (
            inst.get('price_monthly') or 999999,  # Price ascending
            -(inst.get('gpu_memory_gb') or 0),     # VRAM descending (negative for desc)
            -(inst.get('gpu_count') or 0),         # GPU count descending
            inst.get('provider', ''),               # Provider alphabetical
            inst.get('name', '')                    # Name alphabetical
        )
    
    # Sort by composite key
    sorted_instances = sorted(instances, key=lambda x: x['_sort_key'])
    
    # Add rank and clean up
    for i, inst in enumerate(sorted_instances):
        inst['rank'] = i + 1
        del inst['_meets_constraints']
        del inst['_sort_key']
    
    return sorted_instances


def rank_k8s_packages(
    packages: List[Dict[str, Any]],
    query: str
) -> List[Dict[str, Any]]:
    """
    Rank Kubernetes packages deterministically.
    
    Ranking criteria:
    1. Exact name match (highest priority)
    2. Name starts with query
    3. Query in name (case-insensitive)
    4. Query in description
    5. Stars descending (popularity)
    6. Official packages preferred
    7. Name alphabetical (tie-breaker)
    
    Args:
        packages: List of package dictionaries from DB
        query: Search query string
        
    Returns:
        Sorted list of packages with rank field added
    """
    query_lower = query.lower().strip()
    
    for pkg in packages:
        name_lower = (pkg.get('name') or '').lower()
        desc_lower = (pkg.get('description') or '').lower()
        
        # Calculate match score (higher is better)
        if name_lower == query_lower:
            match_score = 1000
        elif name_lower.startswith(query_lower):
            match_score = 900
        elif query_lower in name_lower:
            match_score = 800
        elif query_lower in desc_lower:
            match_score = 700
        else:
            match_score = 0
        
        # Composite sort key
        pkg['_sort_key'] = (
            -match_score,                           # Match score descending
            -(pkg.get('stars') or 0),              # Stars descending
            0 if pkg.get('official') else 1,       # Official first
            name_lower                              # Name alphabetical
        )
    
    # Sort by composite key
    sorted_packages = sorted(packages, key=lambda x: x['_sort_key'])
    
    # Add rank and clean up
    for i, pkg in enumerate(sorted_packages):
        pkg['rank'] = i + 1
        del pkg['_sort_key']
    
    return sorted_packages


def rank_hf_models(
    models: List[Dict[str, Any]],
    relevance_scores: Optional[Dict[str, float]] = None
) -> List[Dict[str, Any]]:
    """
    Rank HuggingFace models deterministically combining relevance and popularity.
    
    Ranking criteria:
    1. Combined score = relevance_weight * relevance + popularity_weight * normalized_popularity
    2. Relevance score from vector similarity (0-1)
    3. Popularity = log(downloads + 1) + log(likes + 1)
    4. Tie-breaker: model_id alphabetical
    
    Weights:
    - Relevance: 0.6
    - Popularity: 0.4
    
    Args:
        models: List of model dictionaries with downloads, likes, etc.
        relevance_scores: Dict mapping model_id to relevance score (0-1)
        
    Returns:
        Sorted list of models with rank and combined_score fields added
    """
    import math
    
    relevance_scores = relevance_scores or {}
    
    # Calculate popularity scores
    max_popularity = 0.0
    for model in models:
        downloads = model.get('downloads') or 0
        likes = model.get('likes') or 0
        popularity = math.log(downloads + 1) + math.log(likes + 1)
        model['_popularity'] = popularity
        max_popularity = max(max_popularity, popularity)
    
    # Normalize and compute combined score
    for model in models:
        model_id = model.get('model_id', '')
        relevance = relevance_scores.get(model_id, 0.5)  # Default 0.5 if missing
        
        # Normalize popularity to 0-1
        norm_popularity = model['_popularity'] / max_popularity if max_popularity > 0 else 0
        
        # Combined score with fixed weights
        combined_score = 0.6 * relevance + 0.4 * norm_popularity
        model['relevance_score'] = round(relevance, 4)
        model['combined_score'] = round(combined_score, 4)
        
        # Sort key (negative for descending, then alphabetical tie-breaker)
        model['_sort_key'] = (
            -combined_score,
            model_id
        )
    
    # Sort by composite key
    sorted_models = sorted(models, key=lambda x: x['_sort_key'])
    
    # Add rank and clean up
    for i, model in enumerate(sorted_models):
        model['rank'] = i + 1
        del model['_popularity']
        del model['_sort_key']
    
    return sorted_models

