import logging

# Import Supabase token verification utilities
from app.core.security import (
    extract_supabase_user_id,
    extract_user_email,
    verify_supabase_token,
)

# Import CRUD operations needed to fetch/create users
from app.crud import crud_user

# Import the database session dependency
from app.db.session import get_db

# Import the User model for type hinting and the internal creation schema
from app.models.user_models import User
from app.schemas.user_schemas import UserCreateInternal
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

logger = logging.getLogger(__name__)

# OAuth2PasswordBearer extracts the token from the 'Authorization: Bearer <token>' header.
# The tokenUrl is primarily for OpenAPI documentation; it doesn't dictate the actual login flow,
# which now happens externally via Supabase on the frontend.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/docs_placeholder"
)  # Placeholder URL for docs


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    FastAPI dependency to:
    1. Verify the Supabase JWT token from the Authorization header.
    2. Extract the Supabase User ID (sub claim).
    3. Find the corresponding user in the local database.
    4. If not found, create a new local user record linked to the Supabase ID.
    5. Return the local User object.

    Raises HTTPException 401 if the token is invalid, expired, or the user cannot be found/created.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },  # Standard header for bearer token auth challenges
    )

    # 1. Verify the token using Supabase JWT Secret and settings
    payload = verify_supabase_token(token)
    if payload is None:
        logger.debug("Token verification failed in get_current_user dependency.")
        raise credentials_exception

    # 2. Extract Supabase User ID (UUID)
    supabase_user_id = extract_supabase_user_id(payload)
    if supabase_user_id is None:
        # Specific error logged within extract_supabase_user_id
        raise credentials_exception

    # 3. Find user in local DB
    user = crud_user.get_user_by_supabase_id(db, supabase_auth_id=supabase_user_id)

    # 4. Create local user if they don't exist (first login sync)
    if user is None:
        logger.info(
            f"User with Supabase ID {supabase_user_id} not found locally. Attempting creation."
        )
        user_email = extract_user_email(payload)
        if not user_email:
            logger.error(
                f"Cannot create local user: Email not found in token for Supabase ID {supabase_user_id}."
            )
            # You might decide to allow creation without email, but it's often essential
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email missing from token.",
            )

        # Defensive check: Does another local user already have this email?
        existing_by_email = crud_user.get_user_by_email(db, email=user_email)
        if existing_by_email:
            # This scenario indicates a potential inconsistency.
            # Option 1: Link existing local user (if not already linked)
            logger.warning(
                f"Supabase user {supabase_user_id} has email {user_email}, which already exists locally for user {existing_by_email.id}. Attempting to link."
            )
            if existing_by_email.supabase_auth_id is None:
                existing_by_email.supabase_auth_id = supabase_user_id
                db.add(existing_by_email)
                user = existing_by_email  # Use the existing, now linked, user
                logger.info(
                    f"Successfully linked existing local user {user.id} to Supabase ID {supabase_user_id}."
                )
            # Option 2: Raise conflict error (Safer if supabase_auth_id should be unique link)
            elif existing_by_email.supabase_auth_id != supabase_user_id:
                logger.error(
                    f"Conflict: Email {user_email} belongs to local user {existing_by_email.id} (Supabase ID: {existing_by_email.supabase_auth_id}), but token is for Supabase ID {supabase_user_id}."
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User email conflict during synchronization.",
                )
            else:  # Already linked correctly
                user = existing_by_email

        # If no email conflict, proceed to create the new local user record
        if (
            user is None
        ):  # Check again in case the email conflict resolution assigned 'user'
            user_create_data = UserCreateInternal(
                supabase_auth_id=supabase_user_id,
                email=user_email,
                # Extract username if available and desired, e.g., from payload.get("user_metadata", {}).get("display_name")
                username=payload.get("user_metadata", {}).get("username", None),
                is_active=True,  # Assume new users are active
            )
            try:
                user = crud_user.create_user_from_supabase(
                    db=db, user_in=user_create_data
                )
                # IMPORTANT: Commit is handled by the get_db dependency wrapper after the endpoint function returns successfully.
                # We need the user object available within the endpoint, so we proceed.
                logger.info(
                    f"Successfully created local user {user.id} for Supabase user {supabase_user_id}."
                )
            except Exception as e:
                logger.error(
                    f"Database error creating local user for Supabase ID {supabase_user_id}: {e}"
                )
                # Rollback will happen in get_db dependency
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to synchronize user profile.",
                )

    # 5. Return the local User object
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency that relies on `get_current_user` and then checks
    if the retrieved user account is marked as active.

    Raises HTTPException 400 if the user is inactive.
    """
    if not crud_user.is_user_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


# Optional: Dependency for Admin Roles (Example Structure)
# def require_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
#     """Checks if the current user has an admin role (requires role implementation)."""
#     # Example: Check an 'is_admin' flag or role relationship on the User model
#     # if not getattr(current_user, 'is_admin', False):
#     #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required.")
#     # For now, just pass through if the check is not implemented
#     # Remove this placeholder logic when implementing real admin checks
#     logger.warning("Admin check bypassed in require_admin_user dependency!")
#     return current_user
