"""HuggingFace model search tool using RAG with pgvector and reranking."""
from typing import Dict, Any, List, Optional
from app.db import execute_query
from app.ranking import rank_hf_models
from app.config import get_settings
from openai import OpenAI

settings = get_settings()
openai_client = OpenAI(api_key=settings.openai_api_key)


def get_query_embedding(text: str) -> List[float]:
    """
    Get embedding for a text query using OpenAI.
    
    Args:
        text: Query text
        
    Returns:
        List of floats representing the embedding vector
    """
    response = openai_client.embeddings.create(
        model=settings.openai_embed_model,
        input=text
    )
    return response.data[0].embedding


def search_hf_models(
    query: str,
    pipeline_tag: Optional[str] = None,
    license_filter: Optional[List[str]] = None,
    top_k: int = None
) -> Dict[str, Any]:
    """
    Search HuggingFace models using RAG (vector search + reranking).
    
    Process:
    1. Embed the query
    2. Vector search on hf.card_chunks
    3. Collapse chunks to card_hash -> models
    4. Join hf.models for metadata (downloads, likes, license, pipeline_tag)
    5. Rerank by relevance + popularity
    6. Apply license/task filters
    7. Return top_k
    
    Args:
        query: Search query
        pipeline_tag: Filter by pipeline tag (e.g., "text-generation")
        license_filter: List of acceptable licenses
        top_k: Number of results to return
        
    Returns:
        Dict with results list and metadata
    """
    top_k = top_k or settings.hf_top_k
    chunk_top_k = settings.hf_chunk_top_k
    
    # 1. Get query embedding
    query_embedding = get_query_embedding(query)
    embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
    
    # 2. Vector search on chunks
    # Find top chunks, then aggregate by card_hash to get relevance scores
    chunk_search_query = """
        WITH ranked_chunks AS (
            SELECT 
                card_hash,
                1 - (embedding <=> %s::vector) as similarity,
                chunk_text
            FROM hf.card_chunks
            WHERE 
                embedding_model_name = %s
                AND chunker_version = %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        ),
        card_scores AS (
            SELECT 
                card_hash,
                MAX(similarity) as max_similarity,
                AVG(similarity) as avg_similarity
            FROM ranked_chunks
            GROUP BY card_hash
        )
        SELECT 
            cs.card_hash,
            cs.max_similarity,
            cs.avg_similarity,
            (cs.max_similarity * 0.7 + cs.avg_similarity * 0.3) as combined_similarity
        FROM card_scores cs
        ORDER BY combined_similarity DESC
        LIMIT 20
    """
    
    params = (
        embedding_str,
        settings.hf_embedding_model_name,
        settings.hf_chunker_version,
        embedding_str,
        chunk_top_k
    )
    
    card_scores = execute_query(chunk_search_query, params)
    
    if not card_scores:
        return {
            "results": [],
            "metadata": {
                "total_found": 0,
                "top_k": top_k,
                "query": query,
                "embedding_model": settings.hf_embedding_model_name
            }
        }
    
    # 3. Map card_hash to models with metadata
    card_hashes = [cs['card_hash'] for cs in card_scores]
    relevance_by_card = {cs['card_hash']: cs['combined_similarity'] for cs in card_scores}
    
    # Build placeholders for IN clause
    placeholders = ','.join(['%s'] * len(card_hashes))
    
    # Build license filter clause
    license_clause = ""
    license_params = []
    if license_filter:
        license_placeholders = ','.join(['%s'] * len(license_filter))
        license_clause = f"AND m.license IN ({license_placeholders})"
        license_params = license_filter
    
    # Build pipeline_tag filter clause
    pipeline_clause = ""
    pipeline_params = []
    if pipeline_tag:
        pipeline_clause = "AND m.pipeline_tag = %s"
        pipeline_params = [pipeline_tag]
    
    model_query = f"""
        SELECT 
            m.model_id::text,
            m.license::text,
            COALESCE(m.likes, 0)::bigint as likes,
            COALESCE(m.downloads, 0)::bigint as downloads,
            m.pipeline_tag::text,
            m.tags,
            mtc.card_hash::text
        FROM hf.model_to_card mtc
        JOIN hf.models m ON m.model_id = mtc.model_id
        WHERE mtc.card_hash IN ({placeholders})
        {license_clause}
        {pipeline_clause}
        ORDER BY m.downloads DESC NULLS LAST
    """
    
    all_params = tuple(card_hashes) + tuple(license_params) + tuple(pipeline_params)
    models = execute_query(model_query, all_params)
    
    # 4. Propagate relevance scores to models
    relevance_scores = {}
    for model in models:
        card_hash = model['card_hash']
        relevance = relevance_by_card.get(card_hash, 0.0)
        relevance_scores[model['model_id']] = relevance
    
    # 5. Rerank by relevance + popularity
    ranked_models = rank_hf_models(models, relevance_scores)
    
    return {
        "results": ranked_models[:top_k],
        "metadata": {
            "total_found": len(ranked_models),
            "top_k": top_k,
            "query": query,
            "embedding_model": settings.hf_embedding_model_name,
            "chunker_version": settings.hf_chunker_version,
            "filters": {
                "pipeline_tag": pipeline_tag,
                "license_filter": license_filter
            }
        }
    }


def format_hf_for_llm(results: List[Dict[str, Any]]) -> str:
    """
    Format HuggingFace model results for LLM consumption.
    
    Args:
        results: List of HF models
        
    Returns:
        Formatted string for LLM
    """
    if not results:
        return "No HuggingFace models found matching the query."
    
    lines = ["Found HuggingFace models (ranked by relevance + popularity):"]
    for r in results:
        license_info = f" | License: {r.get('license', 'Unknown')}"
        pipeline_info = f" | Task: {r.get('pipeline_tag', 'N/A')}"
        stats = f" | {r.get('downloads', 0):,} downloads, {r.get('likes', 0):,} likes"
        relevance = f" | Relevance: {r.get('relevance_score', 0):.2f}"
        
        lines.append(
            f"{r['rank']}. {r['model_id']}{pipeline_info}{license_info}{stats}{relevance}"
        )
    
    return "\n".join(lines)

