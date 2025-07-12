from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from datetime import datetime
import logging

from app.db import get_session
from app.models import User, Tag, UserTagLink
from app.schemas import UserRegistrationRequest, UserRead, ApiKeyResponse, TagRead
from app.auth import generate_api_key_with_hash
from app.dependencies import require_auth

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Access forbidden"},
        404: {"description": "User not found"},
        409: {"description": "User already registered"},
    }
)


@router.post("/register",
             response_model=ApiKeyResponse,
             status_code=201,
             summary="Register user and get API key",
             description="""
    Complete user registration for pre-created users.
    
    **Registration Process:**
    1. User must already exist in database (pre-created by admin)
    2. User provides username that matches database entry
    3. System validates user exists and is not already registered
    4. API key is generated and returned (shown only once)
    5. User account is activated
    
    **Important:** Save the API key immediately - it will not be shown again!
    """,
             responses={
                 201: {
                     "description": "Registration successful",
                     "content": {
                         "application/json": {
                             "example": {
                                 "user_id": 1,
                                 "username": "john_doe",
                                 "api_key": "abcd1234efgh5678ijkl9012mnop3456",
                                 "message": "Registration complete. Save your API key - it won't be shown again."
                             }
                         }
                     }
                 },
                 404: {
                     "description": "Username not found",
                     "content": {
                         "application/json": {
                             "example": {
                                 "detail": "Username 'john_doe' not found. Contact admin to create your account.",
                                 "error_code": "USERNAME_NOT_FOUND"
                             }
                         }
                     }
                 },
                 409: {
                     "description": "User already registered",
                     "content": {
                         "application/json": {
                             "example": {
                                 "detail": "User 'john_doe' is already registered",
                                 "error_code": "USER_ALREADY_REGISTERED"
                             }
                         }
                     }
                 }
             }
             )
async def register_user(
    registration_data: UserRegistrationRequest = Body(
        ...,
        description="User registration data",
        example={
            "username": "john_doe",
            "email": "john@example.com"
        }
    ),
    session: AsyncSession = Depends(get_session)
):
    """Register a pre-existing user and generate API key"""

    logger.info(
        f"Registration attempt for username: {registration_data.username}")

    # Validate username format
    if not registration_data.username or len(registration_data.username.strip()) < 3:
        logger.warning(
            f"Registration failed: Invalid username format '{registration_data.username}'")
        raise HTTPException(
            status_code=422,
            detail="Username must be at least 3 characters long and not empty.",
            headers={"X-Error-Code": "INVALID_USERNAME_FORMAT"}
        )

    # Check if user exists in database
    user_query = select(User).where(
        User.username == registration_data.username.strip())
    user_result = await session.execute(user_query)
    user = user_result.scalar_one_or_none()

    if not user:
        logger.warning(
            f"Registration failed: Username '{registration_data.username}' not found")
        raise HTTPException(
            status_code=404,
            detail=f"Username '{registration_data.username}' not found. Contact admin to create your account.",
            headers={"X-Error-Code": "USERNAME_NOT_FOUND"}
        )

    # Check if user is already registered
    if user.is_registered:
        logger.warning(
            f"Registration failed: User '{registration_data.username}' already registered")
        raise HTTPException(
            status_code=409,
            detail=f"User '{registration_data.username}' is already registered",
            headers={"X-Error-Code": "USER_ALREADY_REGISTERED"}
        )

    # Generate API key and hash
    api_key, key_hash, salt = generate_api_key_with_hash()

    # Update user record
    user.email = registration_data.email or user.email
    user.api_key_hash = key_hash
    user.api_key_salt = salt
    user.is_active = True
    user.is_registered = True
    user.registered_at = datetime.utcnow()

    session.add(user)
    await session.commit()
    await session.refresh(user)

    logger.info(f"Registration successful for user: {user.username}")

    return ApiKeyResponse(
        user_id=user.user_id,
        username=user.username,
        api_key=api_key,
        message="Registration complete. Save your API key - it won't be shown again."
    )


@router.get("/users/me",
            response_model=UserRead,
            summary="Get current user information",
            description="""
    Retrieve information about the currently authenticated user.
    
    **Requires Authentication:** Valid API key in X-API-Key header or Authorization Bearer token
    
    **Returns:** User profile information including tags (excludes sensitive data)
    """,
            response_description="Current user information with tags"
            )
async def get_current_user_info(
    current_user: User = Depends(require_auth),
    session: AsyncSession = Depends(get_session)
):
    """Get current authenticated user information with tags"""

    # Load user tags
    tags_query = select(Tag).join(UserTagLink).where(
        UserTagLink.user_id == current_user.user_id)
    tags_result = await session.execute(tags_query)
    tags = tags_result.scalars().all()

    user_tags = [TagRead(id=tag.id, category=tag.category,
                         tag=tag.tag) for tag in tags]

    return UserRead(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        is_registered=current_user.is_registered,
        created_at=current_user.created_at,
        registered_at=current_user.registered_at,
        last_login=current_user.last_login,
        tags=user_tags
    )


@router.post("/regenerate-key",
             response_model=ApiKeyResponse,
             summary="Regenerate API key",
             description="""
    Generate a new API key for the current user, invalidating the old one.
    
    **Requires Authentication:** Valid API key in X-API-Key header or Authorization Bearer token
    
    **Warning:** This will invalidate your current API key immediately!
    
    **Important:** Save the new API key immediately - it will not be shown again!
    """,
             response_description="New API key (shown only once)",
             responses={
                 200: {
                     "description": "API key regenerated successfully",
                     "content": {
                         "application/json": {
                             "example": {
                                 "user_id": 1,
                                 "username": "john_doe",
                                 "api_key": "new1234key5678goes9012here3456",
                                 "message": "API key regenerated. Save your new key - it won't be shown again."
                             }
                         }
                     }
                 }
             }
             )
async def regenerate_api_key(
    current_user: User = Depends(require_auth),
    session: AsyncSession = Depends(get_session)
):
    """Generate new API key for current user, invalidating the old one"""

    logger.info(f"API key regeneration for user: {current_user.username}")

    # Generate new API key and hash
    new_api_key, new_key_hash, new_salt = generate_api_key_with_hash()

    # Update user with new API key
    current_user.api_key_hash = new_key_hash
    current_user.api_key_salt = new_salt

    session.add(current_user)
    await session.commit()

    logger.info(
        f"API key regenerated successfully for user: {current_user.username}")

    return ApiKeyResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        api_key=new_api_key,
        message="API key regenerated. Save your new key - it won't be shown again."
    )
