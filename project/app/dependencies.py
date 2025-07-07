from fastapi import HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import Optional, Annotated
import logging

from app.db import get_session
from app.models import User
from app.auth import verify_api_key, is_valid_api_key_format

# Set up logging
logger = logging.getLogger(__name__)

# HTTP Bearer scheme for OpenAPI documentation
security = HTTPBearer(auto_error=False)


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Annotated[Optional[str], Header()] = None
) -> User:
    """
    Extract and validate API key from headers, return authenticated user.

    Supports two authentication methods:
    1. X-API-Key header: X-API-Key: <api_key>
    2. Authorization header: Authorization: Bearer <api_key>

    Args:
        session: Database session
        authorization: Bearer token from Authorization header
        x_api_key: API key from X-API-Key header

    Returns:
        User: Authenticated user object

    Raises:
        HTTPException: 401 if authentication fails
    """

    # Extract API key from headers
    api_key = None

    # Try X-API-Key header first
    if x_api_key:
        api_key = x_api_key
        logger.debug("API key extracted from X-API-Key header")

    # Try Authorization header as fallback
    elif authorization and authorization.credentials:
        api_key = authorization.credentials
        logger.debug("API key extracted from Authorization header")

    # No API key provided
    if not api_key:
        logger.warning("Authentication failed: No API key provided")
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Validate API key format
    if not is_valid_api_key_format(api_key):
        logger.warning("Authentication failed: Invalid API key format")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key format",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Find user with matching API key hash
    users_query = select(User).where(
        User.api_key_hash.isnot(None),
        User.is_active,
        User.is_registered
    )
    users_result = await session.execute(users_query)
    users = users_result.scalars().all()

    # Check each active user's API key
    for user in users:
        if user.api_key_hash and user.api_key_salt:
            if verify_api_key(api_key, user.api_key_hash, user.api_key_salt):
                logger.info(
                    f"Authentication successful for user: {user.username}")

                # Update last login timestamp
                from datetime import datetime
                user.last_login = datetime.utcnow()
                session.add(user)
                await session.commit()

                return user

    # No matching user found
    logger.warning("Authentication failed: Invalid API key")
    raise HTTPException(
        status_code=401,
        detail="Invalid API key",
        headers={"WWW-Authenticate": "Bearer"}
    )


async def require_auth(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency wrapper that requires authentication.

    Args:
        current_user: User from get_current_user dependency

    Returns:
        User: Authenticated user object

    Raises:
        HTTPException: 403 if user is not active or registered
    """

    # Double-check user status (should already be verified in get_current_user)
    if not current_user.is_active:
        logger.warning(
            f"Access denied: User {current_user.username} is not active")
        raise HTTPException(
            status_code=403,
            detail="User account is not active"
        )

    if not current_user.is_registered:
        logger.warning(
            f"Access denied: User {current_user.username} is not registered")
        raise HTTPException(
            status_code=403,
            detail="User has not completed registration"
        )

    return current_user


# Optional dependency that allows both authenticated and unauthenticated access
async def get_current_user_optional(
    session: AsyncSession = Depends(get_session),
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Annotated[Optional[str], Header()] = None
) -> Optional[User]:
    """
    Optional authentication dependency that returns None if no valid auth provided.
    Used for endpoints that can work with or without authentication.

    Returns:
        Optional[User]: Authenticated user if valid credentials provided, None otherwise
    """
    try:
        return await get_current_user(session, authorization, x_api_key)
    except HTTPException:
        # Return None for optional authentication
        return None
