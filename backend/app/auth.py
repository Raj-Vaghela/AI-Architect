"""Supabase Auth integration.

Goal:
- Use Supabase Auth JWT access tokens to identify the logged-in user.
- Store chats per user (`chat.conversations.user_id = <jwt sub>`), so users can log in from any device and see history.

How it works:
- Frontend sends `Authorization: Bearer <access_token>` (Supabase session access_token).
- We verify the JWT signature + exp/nbf, then extract `sub` as the user id.

Supported verification modes:
1) **HS256** via `SUPABASE_JWT_SECRET` (most common in Supabase projects).
2) **RS256** via JWKS fetched from `${SUPABASE_PROJECT_URL}/auth/v1/.well-known/jwks.json` when configured.

Dev fallback:
- In development only, we allow `X-User-Id` as a temporary fallback so local scripts can work.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

import httpx
import jwt
from fastapi import Header, HTTPException, Depends

from app.config import get_settings
from app.constants import AuthConfig

_JWKS_CACHE: Dict[str, Any] | None = None
_JWKS_CACHE_AT: float = 0.0


def _get_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) != 2:
        return None
    scheme, token = parts[0].strip(), parts[1].strip()
    if scheme.lower() != "bearer" or not token:
        return None
    return token


def _fetch_jwks(jwks_url: str) -> Dict[str, Any]:
    """
    Fetch JWKS (JSON Web Key Set) from Supabase with caching.
    
    Args:
        jwks_url: URL to fetch JWKS from
        
    Returns:
        JWKS data as dictionary
        
    Raises:
        httpx.HTTPError: If request fails
    """
    global _JWKS_CACHE, _JWKS_CACHE_AT
    now = time.time()
    if _JWKS_CACHE and (now - _JWKS_CACHE_AT) < AuthConfig.JWKS_CACHE_TTL_SECONDS:
        return _JWKS_CACHE

    response = httpx.get(jwks_url, timeout=AuthConfig.HTTP_TIMEOUT_SECONDS)
    response.raise_for_status()
    data = response.json()
    _JWKS_CACHE = data
    _JWKS_CACHE_AT = now
    return data


def _verify_jwt_and_get_sub(token: str) -> str:
    settings = get_settings()

    # Try HS256 first if secret provided
    jwt_secret = getattr(settings, "supabase_jwt_secret", None)
    if jwt_secret:
        try:
            payload = jwt.decode(
                token,
                jwt_secret,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
            sub = payload.get("sub")
            if not sub:
                raise HTTPException(status_code=401, detail="Invalid token: missing sub")
            return str(sub)
        except jwt.PyJWTError:
            # fallthrough to RS256 JWKS if configured
            pass

    # Try asymmetric JWKS (RS256/ES256) if project URL provided
    project_url = getattr(settings, "supabase_project_url", None)
    if project_url:
        jwks_url = project_url.rstrip("/") + "/auth/v1/.well-known/jwks.json"
        try:
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            alg = unverified_header.get("alg")
            jwks = _fetch_jwks(jwks_url)
            keys = jwks.get("keys", [])
            key = next((k for k in keys if k.get("kid") == kid), None)
            if not key:
                raise HTTPException(status_code=401, detail="Invalid token: unknown kid")

            # Use PyJWK to handle different key types (RSA, EC) automatically
            signing_key = jwt.PyJWK(key)
            public_key = signing_key.key
            allowed_algs = ["RS256", "RS384", "RS512", "ES256", "ES384", "ES512"]

            if alg and alg not in allowed_algs:
                raise HTTPException(status_code=401, detail=f"Unsupported token alg: {alg}")

            payload = jwt.decode(
                token,
                public_key,
                algorithms=[alg] if alg else allowed_algs,
                options={"verify_aud": False},
            )
            sub = payload.get("sub")
            if not sub:
                raise HTTPException(status_code=401, detail="Invalid token: missing sub")
            return str(sub)
        except jwt.PyJWTError:
            # fallthrough to remote validation (works even for HS256 without exposing secret)
            pass
        except httpx.HTTPError:
            # fallthrough to remote validation
            pass

        # Remote validation fallback: call Supabase Auth server
        # This works even when the project uses legacy JWT secret (HS256) and you don't have it.
        anon_key = getattr(settings, "supabase_anon_key", None)
        if anon_key:
            try:
                user_url = project_url.rstrip("/") + "/auth/v1/user"
                response = httpx.get(
                    user_url,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "apikey": anon_key,
                    },
                    timeout=AuthConfig.HTTP_TIMEOUT_SECONDS,
                )
                if response.status_code != 200:
                    raise HTTPException(status_code=401, detail="Invalid or expired Supabase token")
                data = response.json()
                user_id = data.get("id")
                if not user_id:
                    raise HTTPException(status_code=401, detail="Invalid token: missing user id")
                return str(user_id)
            except httpx.HTTPError:
                raise HTTPException(status_code=503, detail="Unable to validate token with Supabase Auth")

    raise HTTPException(
        status_code=500,
        detail="Supabase auth not configured. Set SUPABASE_JWT_SECRET (legacy HS256) or SUPABASE_PROJECT_URL (JWKS/remote validation). Optionally set SUPABASE_ANON_KEY for remote validation fallback.",
    )


def get_user_id(
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
) -> str:
    """
    FastAPI dependency: returns the authenticated user id.

    - Preferred: Authorization Bearer <Supabase access_token> → verified JWT → user_id = sub
    - Dev fallback: X-User-Id (only in development)
    """
    token = _get_bearer_token(authorization)
    if token:
        return _verify_jwt_and_get_sub(token)

    settings = get_settings()
    if settings.environment == "development" and x_user_id and x_user_id.strip():
        return x_user_id.strip()

    raise HTTPException(
        status_code=401,
        detail="Missing Authorization Bearer token (Supabase access_token).",
    )


def verify_conversation_access(
    conversation_id: str,
    user_id: str = Depends(get_user_id)
) -> str:
    """
    FastAPI dependency: verify user has access to conversation.
    
    Checks:
    1. Conversation exists in database
    2. Conversation belongs to the authenticated user
    
    Args:
        conversation_id: UUID of the conversation
        user_id: Authenticated user ID (from get_user_id dependency)
        
    Returns:
        conversation_id if valid (for chaining)
        
    Raises:
        HTTPException: 404 if conversation not found, 403 if user doesn't own it
    """
    from app.db import conversation_exists, conversation_belongs_to_user
    
    if not conversation_exists(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    if not conversation_belongs_to_user(conversation_id, user_id):
        raise HTTPException(status_code=403, detail="Conversation does not belong to this user")
    return conversation_id
