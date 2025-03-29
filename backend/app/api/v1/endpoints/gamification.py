# app/api/v1/endpoints/gamification.py

import uuid
from typing import List, Optional, Sequence

# CRUD operations for gamification definitions and leaderboard
from app.crud import crud_gamification

# Database session dependency
from app.db.session import get_db

# Models and Schemas
from app.models.user_models import User  # For auth dependency type hint
from app.schemas.gamification_schemas import (
    BadgeCreate,
    BadgeRead,
    BadgeUpdate,
    LeaderboardEntry,
    UserLevelCreate,
    UserLevelRead,
    UserLevelUpdate,
)

# Authentication dependency
from app.services.auth_service import get_current_active_user
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

# Optional: Admin check dependency
# from app.services.auth_service import require_admin_user

router = APIRouter()

# --- User Levels Management (Admin Required - Placeholder Auth) ---


@router.post(
    "/admin/levels/", response_model=UserLevelRead, status_code=status.HTTP_201_CREATED
)
async def admin_create_new_level(
    *,
    db: Session = Depends(get_db),
    level_in: UserLevelCreate,
    # current_admin: User = Depends(require_admin_user) # Use admin dependency when implemented
    current_user: User = Depends(get_current_active_user),  # Placeholder auth
):
    """
    [Admin Required] Create a new user level definition (e.g., Beginner, Intermediate).
    """
    # Add real authorization check here
    if not current_user.is_active:  # Replace with actual admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    existing_level = crud_gamification.get_level_by_name(db, name=level_in.name)
    if existing_level:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Level with name '{level_in.name}' already exists.",
        )
    level = crud_gamification.create_level(db=db, level_in=level_in)
    return level


@router.get("/levels/", response_model=List[UserLevelRead])
async def read_defined_levels(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = Query(default=50, ge=1, le=100),
):
    """
    Get a list of all defined user levels, ordered by minimum points required. (Public)
    """
    levels: Sequence[UserLevelRead] = crud_gamification.get_levels(
        db, skip=skip, limit=limit
    )
    return levels


@router.put("/admin/levels/{level_id}", response_model=UserLevelRead)
async def admin_update_existing_level(
    level_id: uuid.UUID,
    *,
    db: Session = Depends(get_db),
    level_in: UserLevelUpdate,
    # current_admin: User = Depends(require_admin_user)
    current_user: User = Depends(get_current_active_user),  # Placeholder auth
):
    """
    [Admin Required] Update an existing user level definition.
    """
    if not current_user.is_active:  # Replace with actual admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    db_level = crud_gamification.get_level(db, level_id=level_id)
    if not db_level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Level not found"
        )

    # Check for name conflict if name is being changed
    if level_in.name and level_in.name != db_level.name:
        existing_level = crud_gamification.get_level_by_name(db, name=level_in.name)
        if existing_level and existing_level.id != level_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Level with name '{level_in.name}' already exists.",
            )

    level = crud_gamification.update_level(db=db, db_level=db_level, level_in=level_in)
    return level


@router.delete("/admin/levels/{level_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_existing_level(
    level_id: uuid.UUID,
    *,
    db: Session = Depends(get_db),
    # current_admin: User = Depends(require_admin_user)
    current_user: User = Depends(get_current_active_user),  # Placeholder auth
):
    """
    [Admin Required] Delete an existing user level definition.
    Caution: Ensure users are not referencing this level or handle foreign key constraints.
    """
    if not current_user.is_active:  # Replace with actual admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    deleted_level = crud_gamification.delete_level(db=db, level_id=level_id)
    if not deleted_level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Level not found"
        )
    # Return No Content (204) on successful deletion
    return None


# --- Badges Management (Admin Required - Placeholder Auth) ---


@router.post(
    "/admin/badges/", response_model=BadgeRead, status_code=status.HTTP_201_CREATED
)
async def admin_create_new_badge(
    *,
    db: Session = Depends(get_db),
    badge_in: BadgeCreate,
    # current_admin: User = Depends(require_admin_user)
    current_user: User = Depends(get_current_active_user),  # Placeholder auth
):
    """
    [Admin Required] Create a new badge definition.
    """
    if not current_user.is_active:  # Replace with actual admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    existing_badge = crud_gamification.get_badge_by_name(db, name=badge_in.name)
    if existing_badge:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Badge with name '{badge_in.name}' already exists.",
        )
    badge = crud_gamification.create_badge(db=db, badge_in=badge_in)
    return badge


@router.get("/badges/", response_model=List[BadgeRead])
async def read_defined_badges(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = Query(default=100, ge=1, le=200),
    category: Optional[str] = Query(
        default=None, description="Filter badges by category (case-sensitive)"
    ),
):
    """
    Get a list of all defined badges, optionally filtered by category. (Public)
    """
    badges: Sequence[BadgeRead] = crud_gamification.get_badges(
        db, skip=skip, limit=limit, category=category
    )
    return badges


@router.put("/admin/badges/{badge_id}", response_model=BadgeRead)
async def admin_update_existing_badge(
    badge_id: uuid.UUID,
    *,
    db: Session = Depends(get_db),
    badge_in: BadgeUpdate,
    # current_admin: User = Depends(require_admin_user)
    current_user: User = Depends(get_current_active_user),  # Placeholder auth
):
    """
    [Admin Required] Update an existing badge definition.
    """
    if not current_user.is_active:  # Replace with actual admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    db_badge = crud_gamification.get_badge(db, badge_id=badge_id)
    if not db_badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Badge not found"
        )

    # Check for name conflict if name is being changed
    if badge_in.name and badge_in.name != db_badge.name:
        existing_badge = crud_gamification.get_badge_by_name(db, name=badge_in.name)
        if existing_badge and existing_badge.id != badge_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Badge with name '{badge_in.name}' already exists.",
            )

    badge = crud_gamification.update_badge(db=db, db_badge=db_badge, badge_in=badge_in)
    return badge


@router.delete("/admin/badges/{badge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_existing_badge(
    badge_id: uuid.UUID,
    *,
    db: Session = Depends(get_db),
    # current_admin: User = Depends(require_admin_user)
    current_user: User = Depends(get_current_active_user),  # Placeholder auth
):
    """
    [Admin Required] Delete an existing badge definition.
    Caution: Ensure UserBadgeLinks are handled or FK constraints allow deletion/cascade.
    """
    if not current_user.is_active:  # Replace with actual admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    deleted_badge = crud_gamification.delete_badge(db=db, badge_id=badge_id)
    if not deleted_badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Badge not found"
        )
    # Return No Content (204) on successful deletion
    return None


# --- Public Leaderboard Endpoint ---


@router.get("/leaderboard/", response_model=List[LeaderboardEntry])
async def get_public_leaderboard(
    db: Session = Depends(get_db),
    limit: int = Query(
        default=10, ge=1, le=50, description="Number of top users to display"
    ),
):
    """
    Get the public leaderboard showing top users ranked by points. (Public)
    """
    leaderboard = crud_gamification.get_leaderboard(db, limit=limit)
    return leaderboard
