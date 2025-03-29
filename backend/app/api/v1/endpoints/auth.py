# app/api/v1/endpoints/auth.py

# Import the User model for type hinting
from app.models.user_models import User

# Import the UserRead schema for the response model of /users/me
from app.schemas.user_schemas import UserRead

# Import the dependency that verifies Supabase token and gets the local user
from app.services.auth_service import get_current_active_user
from fastapi import APIRouter, Depends, HTTPException, status

# OAuth2PasswordRequestForm is removed as login is handled by Supabase externally
from sqlmodel import Session

# Import the get_db dependency (though not directly used in these simplified endpoints)
# from app.db.session import get_db

router = APIRouter()

# --- Endpoint for FastAPI-based login (/token) is REMOVED ---
# --- Endpoint for FastAPI-based registration (/register) is REMOVED ---
# User registration and login are handled by the frontend using Supabase client library.
# User synchronization (creating local user) happens implicitly within the
# `get_current_active_user` dependency on the first valid token verification.


@router.get("/users/me", response_model=UserRead)
async def read_users_me(
    # This dependency handles Supabase token verification and local user retrieval/creation
    current_user: User = Depends(get_current_active_user),
):
    """
    Get profile details for the currently authenticated user.

    The user is identified and authenticated based on the valid Supabase JWT
    provided in the 'Authorization: Bearer <token>' header.
    """
    # The `current_user` object is the user record from *your* application's database,
    # linked via the supabase_auth_id extracted from the verified token.
    # The `UserRead` schema ensures only appropriate fields are returned.
    return current_user


# Optional: Placeholder endpoint for OpenAPI documentation if needed
# The `tokenUrl` in `auth_service.oauth2_scheme` points here for Swagger UI,
# but this endpoint itself doesn't perform authentication.
@router.post("/docs_placeholder", include_in_schema=False)
async def docs_placeholder_for_token_url():
    """
    Placeholder endpoint. Authentication is handled externally via Supabase.
    This endpoint exists primarily to satisfy the `tokenUrl` requirement for
    tools like Swagger UI when using OAuth2PasswordBearer, even though the
    actual token exchange doesn't happen here.
    """
    # Return an informative message, but this endpoint should not be called directly
    # by the frontend for authentication.
    return {
        "message": "Authentication handled via Supabase. Provide Supabase JWT in Authorization header.",
        "detail": "This endpoint is a placeholder for documentation purposes.",
    }
