# app/api/v1/endpoints/users.py

import uuid
from typing import List, Sequence  # Use Sequence for DB results

# CRUD operations
from app.crud import crud_roadmap, crud_user

# Database session dependency
from app.db.session import get_db

# Models and Schemas
from app.models.user_models import User
from app.schemas.roadmap_schemas import UserProgressRead  # For progress endpoint
from app.schemas.user_schemas import (  # Use Me schema for details
    UserRead,
    UserReadMe,
    UserUpdate,
)

# Authentication dependency
from app.services.auth_service import get_current_active_user
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

# Optional: Admin check dependency (if implementing roles)
# from app.services.auth_service import require_admin_user

router = APIRouter()

# Note: User creation (registration) is handled via Supabase externally,
# and synchronization happens in the auth_service.get_current_user dependency.


# --- Admin Endpoint Example (Protected) ---
@router.get(
    "/", response_model=List[UserRead], dependencies=[Depends(get_current_active_user)]
)  # Add admin check later
async def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = Query(
        default=100, ge=1, le=200
    ),  # Add validation (ge=greater than or equal)
    # current_admin: User = Depends(require_admin_user), # Use admin dependency when implemented
):
    """
    [Admin Required - Placeholder Auth] Retrieve a list of users.
    Requires authentication, add admin role check for production.
    """
    users: Sequence[User] = crud_user.get_users(db, skip=skip, limit=limit)
    return users


# --- Currently Authenticated User Endpoints ---


@router.get("/me/details", response_model=UserReadMe)
async def read_user_me_details(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed profile information for the currently authenticated user,
    including points, level, badges, and streak.
    """
    # Fetch related gamification data. CRUD functions can use eager loading.
    badges_links = crud_user.get_user_badges(db=db, user_id=current_user.id)
    streak_data = crud_user.get_or_create_user_streak(db=db, user_id=current_user.id)
    # The current_user object might already have the level loaded depending on session state,
    # but explicitly fetch if needed or ensure loaded in get_current_user if critical.
    # level_info = crud_gamification.get_level(db, current_user.level_id) if current_user.level_id else None

    # Use the dedicated UserReadMe schema which includes fields for related data
    # SQLModel/Pydantic will attempt to map the relationships.
    # Ensure the relationships (badges, streaks, level) are loaded on the current_user object
    # or construct the response manually if needed.
    user_details = UserReadMe.model_validate(current_user)  # Validate base fields

    # Manually populate relationship fields if not automatically handled by model_validate
    user_details.badges = [
        {"badge": badge_link.badge, "awarded_at": badge_link.awarded_at}
        for badge_link in badges_links
    ]
    user_details.streak = streak_data
    # user_details.level = level_info # Assign loaded level info if needed

    return user_details


@router.put("/me", response_model=UserRead)
async def update_user_me(
    *,  # Enforce keyword arguments for clarity
    db: Session = Depends(get_db),
    user_in: UserUpdate,  # Use the update schema for request body
    current_user: User = Depends(get_current_active_user),
):
    """
    Update the profile information (email, username) for the currently authenticated user.
    Password updates are handled by Supabase.
    """
    # Check for potential conflicts if email or username are being changed
    if user_in.email and user_in.email != current_user.email:
        existing_email_user = crud_user.get_user_by_email(db, email=user_in.email)
        if existing_email_user and existing_email_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered by another user.",
            )
    if user_in.username and user_in.username != current_user.username:
        existing_username_user = crud_user.get_user_by_username(
            db, username=user_in.username
        )
        if existing_username_user and existing_username_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken.",
            )

    updated_user = crud_user.update_user(db=db, db_user=current_user, user_in=user_in)
    return updated_user


# --- User Progress Endpoint ---
@router.get("/me/progress", response_model=List[UserProgressRead])
async def read_my_progress(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """
    Get all progress tracking items (completed resources, modules, quiz/assignment links)
    for the currently authenticated user.
    """
    progress_items: Sequence[UserProgressRead] = crud_roadmap.get_user_progress_all(
        db=db, user_id=current_user.id
    )
    return progress_items


# --- Public User Profile (Optional) ---
@router.get("/{user_id}", response_model=UserRead)
async def read_user_by_id(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    # Optionally require authentication even to view public profiles
    # current_viewer: User = Depends(get_current_active_user)
):
    """
    Get basic public profile information for a specific user by their internal ID.
    """
    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None or not db_user.is_active:  # Don't show inactive users
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    # Return basic info using UserRead schema
    return db_user
