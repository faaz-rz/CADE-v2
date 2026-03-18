"""
Auth0 JWT Verification — FastAPI dependency for token validation and role gating.

Uses PyJWKClient to fetch Auth0's JWKS and verify RS256-signed tokens.
"""

import os
import logging
from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient

logger = logging.getLogger(__name__)

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", "")
AUTH0_AUDIENCE = os.environ.get("AUTH0_API_AUDIENCE", "")
ROLE_CLAIM = "https://capitalrisk.app/role"

security = HTTPBearer()


@lru_cache()
def _get_jwks_client() -> PyJWKClient:
    """Cached JWKS client — avoids re-fetching keys on every request."""
    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    return PyJWKClient(jwks_url)


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Validate the Bearer token from Auth0.
    Returns the decoded JWT payload on success.
    Raises 401 on any validation failure.
    """
    token = credentials.credentials
    try:
        jwks_client = _get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=AUTH0_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Unable to verify token: {str(e)}",
        )


def require_role(*allowed_roles: str):
    """
    Factory that returns a FastAPI dependency which checks
    the user's role claim against the allowed list.

    Usage:
        @router.post("/upload")
        async def upload(payload: dict = Depends(require_role("ANALYST", "ADMIN"))):
    """
    async def checker(payload: dict = Depends(verify_token)) -> dict:
        role = payload.get(ROLE_CLAIM, "VIEWER")
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' is not permitted. Required: {', '.join(allowed_roles)}",
            )
        return payload

    return checker
