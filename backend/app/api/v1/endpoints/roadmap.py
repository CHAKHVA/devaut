# app/api/v1/endpoints/roadmaps.py

import uuid
from typing import List, Optional, Sequence

# CRUD operations for roadmaps and related items
from app.crud import crud_roadmap

# Database session dependency
from app.db.session import get_db
from app.models.user_models import User  # Import User model for dependency type hint

# Schemas used in request bodies and response models
from app.schemas.roadmap_schemas import (
    AssignmentCreate,
    AssignmentRead,
    AssignmentUpdate,
    LearningResourceCreate,
    LearningResourceRead,
    LearningResourceUpdate,
    QuizCreate,
    QuizQuestionCreate,
    QuizQuestionRead,
    QuizQuestionUpdate,
    QuizRead,
    QuizUpdate,
    RoadmapCreate,
    RoadmapModuleCreate,
    RoadmapModuleRead,
    RoadmapModuleUpdate,
    RoadmapRead,
    RoadmapReadWithDetails,
    RoadmapUpdate,
)

# Authentication dependency (apply where needed)
from app.services.auth_service import get_current_active_user
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

# Optional: Admin check dependency
# from app.services.auth_service import require_admin_user


router = APIRouter()

# ==============================================================================
# Roadmap Endpoints
# ==============================================================================


@router.post(
    "/",
    response_model=RoadmapRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create New Roadmap",
)
async def create_new_roadmap(
    *,  # Enforce keyword-only arguments
    db: Session = Depends(get_db),
    roadmap_in: RoadmapCreate,
    # Protect this endpoint - Example: require admin privileges
    # current_admin: User = Depends(require_admin_user),
    current_user: User = Depends(get_current_active_user),  # Placeholder: Requires auth
):
    """
    Create a new learning roadmap.

    - Allows nested creation of modules and their items (resources, assignments, quizzes, questions)
      if included in the request body.
    - **Requires Admin Role** (Placeholder Auth: requires authenticated user for now).
    """
    # Add proper authorization check here
    if not current_user.is_active:  # Replace with actual admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    roadmap = crud_roadmap.create_roadmap(db=db, roadmap_in=roadmap_in)
    return roadmap


@router.get("/", response_model=List[RoadmapRead], summary="List Roadmaps")
async def read_all_roadmaps(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = Query(
        default=50, ge=1, le=100, description="Number of roadmaps to return per page."
    ),
    topic: Optional[str] = Query(
        default=None, description="Filter roadmaps by topic (case-sensitive)."
    ),
):
    """
    Retrieve a list of available learning roadmaps.

    - Supports pagination using `skip` and `limit`.
    - Allows optional filtering by `topic`.
    - This endpoint is **Public**.
    """
    roadmaps: Sequence[RoadmapRead] = crud_roadmap.get_roadmaps(
        db, skip=skip, limit=limit, topic=topic
    )
    return roadmaps


@router.get(
    "/{roadmap_id}",
    response_model=RoadmapReadWithDetails,
    summary="Get Roadmap Details",
)
async def read_single_roadmap(
    roadmap_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """
    Get detailed information for a specific roadmap by its ID.

    - Includes all nested modules, resources, assignments, quizzes, and questions.
    - This endpoint is **Public**.
    """
    # Use the CRUD function that eagerly loads details
    db_roadmap = crud_roadmap.get_roadmap_with_details(db, roadmap_id=roadmap_id)
    if db_roadmap is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found"
        )
    return db_roadmap


@router.put("/{roadmap_id}", response_model=RoadmapRead, summary="Update Roadmap Info")
async def update_existing_roadmap(
    roadmap_id: uuid.UUID,
    *,
    db: Session = Depends(get_db),
    roadmap_in: RoadmapUpdate,  # Only includes fields to update roadmap itself
    # Protect this endpoint
    # current_admin: User = Depends(require_admin_user),
    current_user: User = Depends(get_current_active_user),  # Placeholder: Requires auth
):
    """
    Update an existing roadmap's core details (title, description, topic, active status).

    - Does not handle updating nested modules/items via this endpoint. Use module/item specific endpoints for that.
    - **Requires Admin Role** (Placeholder Auth: requires authenticated user for now).
    """
    if not current_user.is_active:  # Replace with actual admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    db_roadmap = crud_roadmap.get_roadmap(db, roadmap_id=roadmap_id)
    if db_roadmap is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found"
        )

    # Add authorization check here if needed (e.g., owner or admin)
    updated_roadmap = crud_roadmap.update_roadmap(
        db=db, db_roadmap=db_roadmap, roadmap_in=roadmap_in
    )
    return updated_roadmap


@router.delete(
    "/{roadmap_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Roadmap"
)
async def delete_single_roadmap(
    roadmap_id: uuid.UUID,
    *,
    db: Session = Depends(get_db),
    # Protect this endpoint
    # current_admin: User = Depends(require_admin_user),
    current_user: User = Depends(get_current_active_user),  # Placeholder: Requires auth
):
    """
    Delete a roadmap by its ID.

    - **Requires Admin Role** (Placeholder Auth: requires authenticated user for now).
    - **Warning**: Ensure database foreign keys are configured for cascading deletes or handle deletion of related items manually/in service layer to avoid errors.
    """
    if not current_user.is_active:  # Replace with actual admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    deleted_roadmap = crud_roadmap.delete_roadmap(db=db, roadmap_id=roadmap_id)
    if not deleted_roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found"
        )
    # No content is returned on successful deletion (HTTP 204)
    return None


# ==============================================================================
# Roadmap Module Endpoints
# ==============================================================================


@router.post(
    "/{roadmap_id}/modules/",
    response_model=RoadmapModuleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add Module to Roadmap",
)
async def create_new_module_for_roadmap(
    roadmap_id: uuid.UUID,
    *,
    db: Session = Depends(get_db),
    module_in: RoadmapModuleCreate,
    # Protect this endpoint
    # current_admin: User = Depends(require_admin_user),
    current_user: User = Depends(get_current_active_user),  # Placeholder: Requires auth
):
    """
    Create a new module and associate it with an existing roadmap.

    - Allows nested creation of resources, assignments, quizzes within the module.
    - **Requires Admin Role** (Placeholder Auth: requires authenticated user for now).
    """
    if not current_user.is_active:  # Replace with actual admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    # Check if roadmap exists
    db_roadmap = crud_roadmap.get_roadmap(db, roadmap_id=roadmap_id)
    if not db_roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found"
        )

    # Pass the roadmap object for relationship linking in CRUD
    module = crud_roadmap.create_module_for_roadmap(
        db=db, module_in=module_in, roadmap_id=roadmap_id, roadmap_obj=db_roadmap
    )
    # Eager load details for the response if the Read schema expects them
    # (This might require a get_module_with_details function)
    # For now, assume RoadmapModuleRead can handle lazy loading or basic fields.
    return module


@router.get(
    "/{roadmap_id}/modules/",
    response_model=List[RoadmapModuleRead],
    summary="List Roadmap Modules",
)
async def read_roadmap_modules_list(
    roadmap_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """
    Get a list of all modules belonging to a specific roadmap, ordered by the 'order' field.
    (Public)
    """
    # Optional: Check if roadmap exists first, return 404 if not
    # db_roadmap = crud_roadmap.get_roadmap(db, roadmap_id=roadmap_id)
    # if not db_roadmap:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")

    modules: Sequence[RoadmapModuleRead] = crud_roadmap.get_modules_for_roadmap(
        db=db, roadmap_id=roadmap_id
    )
    return modules


# It's generally better practice to have module updates/deletes target the module ID directly
# e.g., PUT /modules/{module_id} instead of PUT /roadmaps/{roadmap_id}/modules/{module_id}
# But we can add them here if preferred structure.


@router.put(
    "/modules/{module_id}",  # Targeting module ID directly
    response_model=RoadmapModuleRead,
    summary="Update Module Info",
)
async def update_existing_module(
    module_id: uuid.UUID,
    *,
    db: Session = Depends(get_db),
    module_in: RoadmapModuleUpdate,
    # Protect this endpoint
    # current_admin: User = Depends(require_admin_user),
    current_user: User = Depends(get_current_active_user),  # Placeholder: Requires auth
):
    """
    Update an existing module's details (title, order).

    - **Requires Admin Role** (Placeholder Auth: requires authenticated user for now).
    """
    if not current_user.is_active:  # Replace with actual admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    db_module = crud_roadmap.get_module(db, module_id=module_id)
    if not db_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )

    updated_module = crud_roadmap.update_module(
        db=db, db_module=db_module, module_in=module_in
    )
    return updated_module


@router.delete(
    "/modules/{module_id}",  # Targeting module ID directly
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Module",
)
async def delete_existing_module(
    module_id: uuid.UUID,
    *,
    db: Session = Depends(get_db),
    # Protect this endpoint
    # current_admin: User = Depends(require_admin_user),
    current_user: User = Depends(get_current_active_user),  # Placeholder: Requires auth
):
    """
    Delete a module by its ID.

    - **Requires Admin Role** (Placeholder Auth: requires authenticated user for now).
    - **Warning**: Ensure related items (resources, assignments, quizzes) are handled
      via cascade deletes or manual deletion.
    """
    if not current_user.is_active:  # Replace with actual admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    deleted_module = crud_roadmap.delete_module(db=db, module_id=module_id)
    if not deleted_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )
    return None


# ==============================================================================
# Learning Resource Endpoints (Example - Target Module ID)
# ==============================================================================


@router.post(
    "/modules/{module_id}/resources/",
    response_model=LearningResourceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add Resource to Module",
)
async def create_new_resource_for_module(
    module_id: uuid.UUID,
    *,
    db: Session = Depends(get_db),
    resource_in: LearningResourceCreate,
    # Protect this endpoint
    current_user: User = Depends(get_current_active_user),  # Placeholder: Requires auth
):
    """
    Create a new learning resource and associate it with an existing module.

    - **Requires Admin Role** (Placeholder Auth: requires authenticated user for now).
    """
    if not current_user.is_active:  # Replace with actual admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    db_module = crud_roadmap.get_module(db, module_id=module_id)
    if not db_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )

    resource = crud_roadmap.create_resource_for_module(
        db=db, resource_in=resource_in, module_id=module_id, module_obj=db_module
    )
    return resource


# Add PUT /resources/{resource_id}, DELETE /resources/{resource_id} similarly


# ==============================================================================
# Assignment Endpoints (Example - Target Module ID)
# ==============================================================================


@router.post(
    "/modules/{module_id}/assignments/",
    response_model=AssignmentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add Assignment to Module",
)
async def create_new_assignment_for_module(
    module_id: uuid.UUID,
    *,
    db: Session = Depends(get_db),
    assignment_in: AssignmentCreate,
    # Protect this endpoint
    current_user: User = Depends(get_current_active_user),  # Placeholder: Requires auth
):
    """
    Create a new assignment and associate it with an existing module.

    - **Requires Admin Role** (Placeholder Auth: requires authenticated user for now).
    """
    if not current_user.is_active:  # Replace with actual admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    db_module = crud_roadmap.get_module(db, module_id=module_id)
    if not db_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )

    assignment = crud_roadmap.create_assignment_for_module(
        db=db, assignment_in=assignment_in, module_id=module_id, module_obj=db_module
    )
    return assignment


# Add PUT /assignments/{assignment_id}, DELETE /assignments/{assignment_id} similarly


# ==============================================================================
# Quiz & Question Endpoints (Example - Target Module/Quiz ID)
# ==============================================================================


@router.post(
    "/modules/{module_id}/quizzes/",
    response_model=QuizRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add Quiz to Module",
)
async def create_new_quiz_for_module(
    module_id: uuid.UUID,
    *,
    db: Session = Depends(get_db),
    quiz_in: QuizCreate,  # Can include nested questions
    # Protect this endpoint
    current_user: User = Depends(get_current_active_user),  # Placeholder: Requires auth
):
    """
    Create a new quiz (optionally with questions) and associate it with an existing module.

    - **Requires Admin Role** (Placeholder Auth: requires authenticated user for now).
    """
    if not current_user.is_active:  # Replace with actual admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    db_module = crud_roadmap.get_module(db, module_id=module_id)
    if not db_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )

    quiz = crud_roadmap.create_quiz_for_module(
        db=db, quiz_in=quiz_in, module_id=module_id, module_obj=db_module
    )
    # Eager load questions if QuizRead schema expects them immediately
    # db.refresh(quiz, attribute_names=["questions"]) # Example refresh
    # Or use a get_quiz_with_questions call if needed
    return quiz


@router.post(
    "/quizzes/{quiz_id}/questions/",
    response_model=QuizQuestionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add Question to Quiz",
)
async def create_new_question_for_quiz(
    quiz_id: uuid.UUID,
    *,
    db: Session = Depends(get_db),
    question_in: QuizQuestionCreate,
    # Protect this endpoint
    current_user: User = Depends(get_current_active_user),  # Placeholder: Requires auth
):
    """
    Create a new question and associate it with an existing quiz.

    - **Requires Admin Role** (Placeholder Auth: requires authenticated user for now).
    """
    if not current_user.is_active:  # Replace with actual admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    db_quiz = crud_roadmap.get_quiz(db, quiz_id=quiz_id)
    if not db_quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found"
        )

    question = crud_roadmap.create_question_for_quiz(
        db=db, question_in=question_in, quiz_id=quiz_id, quiz_obj=db_quiz
    )
    return question


@router.put(
    "/quizzes/{quiz_id}",
    response_model=QuizRead,
    summary="Update Quiz Info",
)
async def update_existing_quiz(
    quiz_id: uuid.UUID,
    *,
    db: Session = Depends(get_db),
    quiz_in: QuizUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """
    Update an existing quiz's base fields (title, points_reward).

    - Does not update questions via this endpoint. Use the question-specific endpoints for that.
    - **Requires Admin Role** (Placeholder Auth: requires authenticated user for now).
    """
    if not current_user.is_active:  # Replace with actual admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    db_quiz = crud_roadmap.get_quiz(db, quiz_id=quiz_id)
    if not db_quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found"
        )

    updated_quiz = crud_roadmap.update_quiz(db=db, db_quiz=db_quiz, quiz_in=quiz_in)
    return updated_quiz


@router.delete(
    "/quizzes/{quiz_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Quiz",
)
async def delete_existing_quiz(
    quiz_id: uuid.UUID,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a quiz by its ID.

    - **Requires Admin Role** (Placeholder Auth: requires authenticated user for now).
    - **Warning**: Ensure related questions and user attempts are handled appropriately
      via cascade deletes or manual deletion.
    """
    if not current_user.is_active:  # Replace with actual admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    deleted_quiz = crud_roadmap.delete_quiz(db=db, quiz_id=quiz_id)
    if not deleted_quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found"
        )
    return None


@router.put(
    "/questions/{question_id}",
    response_model=QuizQuestionRead,
    summary="Update Quiz Question",
)
async def update_existing_question(
    question_id: uuid.UUID,
    *,
    db: Session = Depends(get_db),
    question_in: QuizQuestionUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """
    Update an existing quiz question's details.

    - **Requires Admin Role** (Placeholder Auth: requires authenticated user for now).
    """
    if not current_user.is_active:  # Replace with actual admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    db_question = crud_roadmap.get_question(db, question_id=question_id)
    if not db_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        )

    updated_question = crud_roadmap.update_question(
        db=db, db_question=db_question, question_in=question_in
    )
    return updated_question


@router.delete(
    "/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Quiz Question",
)
async def delete_existing_question(
    question_id: uuid.UUID,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a quiz question by its ID.

    - **Requires Admin Role** (Placeholder Auth: requires authenticated user for now).
    """
    if not current_user.is_active:  # Replace with actual admin role check
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required."
        )

    deleted_question = crud_roadmap.delete_question(db=db, question_id=question_id)
    if not deleted_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        )
    return None
