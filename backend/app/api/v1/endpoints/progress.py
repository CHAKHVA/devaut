# app/api/v1/endpoints/progress.py

import uuid
from typing import Dict, List, Optional

# Database session dependency
from app.db.session import get_db
from app.models.roadmap_models import ItemTypeEnum  # Import Enum

# Models and Schemas
from app.models.user_models import User
from app.schemas.roadmap_schemas import (
    UserAssignmentSubmissionCreate,
    UserAssignmentSubmissionRead,
    UserAssignmentSubmissionUpdate,
    UserProgressRead,
    UserQuizAttemptCreate,
    UserQuizAttemptRead,
)

# Service layer for business logic
from app.services import progress_service

# Authentication dependency
from app.services.auth_service import get_current_active_user
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlmodel import Session

# Optional: Admin dependency for grading
# from app.services.auth_service import require_admin_user

router = APIRouter()

# --- Mark Items as Complete ---


@router.post(
    "/complete/resource/{resource_id}",
    response_model=UserProgressRead,
    status_code=status.HTTP_201_CREATED,
)
async def mark_learning_resource_complete(
    resource_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Mark a specific learning resource as completed for the currently authenticated user.
    Creates a UserProgress record and updates daily streak.
    """
    progress = progress_service.mark_item_complete(
        db, user=current_user, item_id=resource_id, item_type=ItemTypeEnum.RESOURCE
    )
    if progress is None:
        # Service layer should ideally raise specific exceptions for not found etc.
        # For now, assume None means an internal error occurred.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark resource as complete.",
        )
    return progress


@router.post(
    "/complete/module/{module_id}",
    response_model=UserProgressRead,
    status_code=status.HTTP_201_CREATED,
)
async def mark_roadmap_module_complete(
    module_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Mark a specific roadmap module as completed for the currently authenticated user.
    Creates a UserProgress record, awards points, and updates daily streak.
    """
    # Optional: Add service layer logic to check if all items in module are complete first
    progress = progress_service.mark_item_complete(
        db, user=current_user, item_id=module_id, item_type=ItemTypeEnum.MODULE
    )
    if progress is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark module as complete.",
        )
    return progress


# --- Quiz Submission ---


@router.post(
    "/quizzes/{quiz_id}/submit",
    response_model=UserQuizAttemptRead,
    status_code=status.HTTP_201_CREATED,
)
async def submit_quiz_attempt(
    quiz_id: uuid.UUID,
    *,
    # Use Body(..., embed=True) if you want the answers under a key like {"answers": {...}}
    # Otherwise, just use the schema directly for the body.
    attempt_in: UserQuizAttemptCreate,  # Expects {"quiz_id": "...", "answers": {...}}
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Submit answers for a specific quiz.
    Calculates score, records attempt, updates progress & gamification status.
    """
    # Optional: Validate quiz_id in path matches body if needed, but schema only needs answers here.
    # if attempt_in.quiz_id != quiz_id: ... error ...

    try:
        attempt_result = progress_service.submit_quiz(
            db, user=current_user, quiz_id=quiz_id, answers=attempt_in.answers
        )
        if attempt_result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process quiz submission.",
            )
        return attempt_result
    except ValueError as e:  # Catch errors like "Quiz not found" from service
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Assignment Submission & Grading ---


@router.post(
    "/assignments/{assignment_id}/submit",
    response_model=UserAssignmentSubmissionRead,
    status_code=status.HTTP_201_CREATED,
)
async def submit_new_assignment(
    assignment_id: uuid.UUID,
    *,
    submission_in: UserAssignmentSubmissionCreate,  # Expects {"assignment_id": "...", "submission_content": "..."}
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Submit content (e.g., URL, text) for a specific assignment.
    Records submission, updates progress, awards partial points, updates streak.
    """
    # Validate assignment ID match between path and body
    if submission_in.assignment_id != assignment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assignment ID in path does not match assignment ID in request body.",
        )

    try:
        submission = progress_service.submit_assignment(
            db=db,
            user=current_user,
            assignment_id=assignment_id,
            submission_content=submission_in.submission_content,
        )
        if submission is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record assignment submission.",
            )
        return submission
    except ValueError as e:  # Catch errors like "Assignment not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Grading Endpoint (Admin/Protected) ---
@router.patch(
    "/submissions/{submission_id}/grade", response_model=UserAssignmentSubmissionRead
)
async def grade_assignment_submission(
    submission_id: uuid.UUID,
    *,
    update_in: UserAssignmentSubmissionUpdate,  # Expects {"status": "...", "grade": ..., "feedback": ...}
    db: Session = Depends(get_db),
    # Add admin authorization check dependency
    # current_admin: User = Depends(require_admin_user),
    current_user: User = Depends(get_current_active_user),  # Placeholder auth
):
    """
    [Admin Required - Placeholder Auth] Grade a specific assignment submission.
    Updates status, grade, feedback, and awards points/badges if passed.
    """
    # Add proper admin role check here
    if not current_user.is_active:  # Replace with real admin check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    try:
        graded_submission = progress_service.grade_assignment(
            db=db,
            submission_id=submission_id,
            status=update_in.status,  # type: ignore # Status might be None, handle in service
            grade=update_in.grade,
            feedback=update_in.feedback,
        )
        if graded_submission is None:
            # Handle cases where grading failed internally in the service
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to grade submission.",
            )
        return graded_submission
    except ValueError as e:  # Catch errors like "Submission not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
