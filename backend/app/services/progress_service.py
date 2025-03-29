# app/services/progress_service.py

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

# Import CRUD operations
from app.crud import (  # crud_user needed for fetching user if grading
    crud_roadmap,
    crud_user,
)

# Import necessary models and schemas
from app.models.roadmap_models import (
    Assignment,
    ItemTypeEnum,
    Quiz,
    QuizQuestion,
    UserProgress,
)

# Import User model for type hinting
from app.models.user_models import User
from app.schemas.roadmap_schemas import (
    UserQuizAttemptCreate,  # Body schema for quiz submission
)
from sqlmodel import Session, select

# Import other services this one interacts with
from . import gamification_service  # Use relative import within services package

logger = logging.getLogger(__name__)


def mark_item_complete(
    db: Session, user: User, item_id: uuid.UUID, item_type: ItemTypeEnum
) -> Optional[UserProgress]:
    """
    Marks a generic learning item (Resource, Module) as complete for a user.
    Creates/updates a UserProgress record and updates the daily streak.
    """
    logger.info(
        f"Attempting to mark item {item_id} ({item_type.value}) complete for user {user.id}"
    )
    try:
        # Create/update the specific progress record for this item
        progress_in = crud_roadmap.UserProgressCreate(
            user_id=user.id,
            item_id=item_id,
            item_type=item_type,
            completed_at=datetime.utcnow(),  # Mark completion time now
        )
        progress = crud_roadmap.create_user_progress(db=db, progress_in=progress_in)

        # Update the user's daily streak (safe to call even if already updated today)
        gamification_service.update_daily_streak(db=db, user=user)

        # Award points? (Example: Award points only for completing modules)
        if item_type == ItemTypeEnum.MODULE:
            # Fetch module title for reason if desired
            module = crud_roadmap.get_module(db, item_id)
            module_title = module.title if module else f"Module {item_id}"
            gamification_service.award_points(
                db=db,
                user=user,
                points_to_add=5,
                reason=f"Module completed: {module_title}",
            )

        return progress

    except Exception as e:
        logger.error(f"Error marking item {item_id} complete for user {user.id}: {e}")
        return None


def submit_quiz(
    db: Session, user: User, quiz_id: uuid.UUID, answers: Dict[str, List[str]]
) -> Optional[crud_roadmap.UserQuizAttempt]:
    """
    Processes a user's quiz submission:
    1. Calculates the score.
    2. Creates a UserQuizAttempt record.
    3. Creates/updates a UserProgress record for the quiz.
    4. Awards points based on score/passing.
    5. Updates daily streak.
    6. Checks for related badges.
    Returns the created UserQuizAttempt record or None on error.
    """
    logger.info(f"Processing quiz {quiz_id} submission for user {user.id}")
    try:
        # 1. Fetch Quiz and its Questions
        quiz = crud_roadmap.get_quiz_with_questions(db, quiz_id=quiz_id)
        if not quiz:
            logger.error(f"Quiz {quiz_id} not found during submission.")
            raise ValueError(
                "Quiz not found"
            )  # Raise specific error for endpoint to catch

        # 2. Calculate Score
        score = 0.0
        if quiz.questions:
            correct_answers_count = 0
            for q in quiz.questions:
                user_answer_keys = answers.get(str(q.id), [])
                # Use sets for order-independent comparison of selected keys
                if set(user_answer_keys) == set(q.correct_option_keys):
                    correct_answers_count += 1
            score = correct_answers_count / len(quiz.questions)
        else:
            logger.warning(f"Quiz {quiz_id} has no questions. Score is 0.")

        # Determine pass status (e.g., score >= 70%)
        passed = score >= 0.7
        logger.info(
            f"Quiz {quiz_id} score for user {user.id}: {score:.2f}, Passed: {passed}"
        )

        # 3. Create UserQuizAttempt record
        attempt_in = UserQuizAttemptCreate(quiz_id=quiz_id, answers=answers)
        attempt = crud_roadmap.create_quiz_attempt(
            db=db, user_id=user.id, attempt_in=attempt_in, score=score, passed=passed
        )

        # 4. Create/Update UserProgress record for the quiz itself
        progress_in = crud_roadmap.UserProgressCreate(
            user_id=user.id,
            item_id=quiz_id,
            item_type=ItemTypeEnum.QUIZ,
            completed_at=attempt.completed_at,  # Use attempt completion time
            meta_data={"attempt_id": str(attempt.id), "score": score, "passed": passed},
        )
        crud_roadmap.create_user_progress(db=db, progress_in=progress_in)

        # 5. Award Points (using gamification_service)
        points_to_award = 0
        reason = ""
        if passed:
            # Base points for passing + bonus based on score
            points_to_award = quiz.points_reward + int(score * 5)  # Example scoring
            reason = f"Quiz passed: {quiz.title}"
        elif score > 0:
            # Award some points even if failed, proportional to score
            points_to_award = int(
                score * quiz.points_reward * 0.5
            )  # Example: half points based on score %
            reason = f"Quiz partial score: {quiz.title}"

        if points_to_award > 0:
            gamification_service.award_points(
                db=db, user=user, points_to_add=points_to_award, reason=reason
            )

        # 6. Update Daily Streak
        gamification_service.update_daily_streak(db=db, user=user)

        # 7. Check for Badges
        if passed:
            # Award general quiz badge
            gamification_service.check_and_award_badge(
                db=db, user=user, badge_name="Quiz Taker"
            )
            # Award perfect score badge
            if score == 1.0:
                gamification_service.check_and_award_badge(
                    db=db, user=user, badge_name="Perfect Score"
                )
            # Award topic-specific badge based on quiz.module.roadmap.topic? (More complex logic)

        return attempt

    except ValueError as ve:  # Catch specific expected errors
        logger.warning(f"Value error during quiz submission: {ve}")
        raise  # Re-raise for the endpoint to handle (e.g., return 404)
    except Exception as e:
        logger.error(
            f"Error submitting quiz {quiz_id} for user {user.id}: {e}", exc_info=True
        )
        # Don't re-raise generic Exception, return None or let endpoint return 500
        return None


def submit_assignment(
    db: Session, user: User, assignment_id: uuid.UUID, submission_content: str
) -> Optional[crud_roadmap.UserAssignmentSubmission]:
    """
    Handles a user's assignment submission:
    1. Creates a UserAssignmentSubmission record.
    2. Creates/updates a UserProgress record for the assignment (status 'submitted').
    3. Awards partial points for submission.
    4. Updates daily streak.
    Returns the created UserAssignmentSubmission record or None on error.
    """
    logger.info(f"Processing assignment {assignment_id} submission for user {user.id}")
    try:
        # 1. Fetch Assignment (to get points info and ensure it exists)
        assignment = crud_roadmap.get_assignment(db, assignment_id=assignment_id)
        if not assignment:
            logger.error(f"Assignment {assignment_id} not found during submission.")
            raise ValueError("Assignment not found")

        # 2. Create UserAssignmentSubmission record
        submission_in = crud_roadmap.UserAssignmentSubmissionCreate(
            assignment_id=assignment_id, submission_content=submission_content
        )
        submission = crud_roadmap.create_assignment_submission(
            db=db, user_id=user.id, submission_in=submission_in
        )

        # 3. Create/Update UserProgress record
        progress_in = crud_roadmap.UserProgressCreate(
            user_id=user.id,
            item_id=assignment_id,
            item_type=ItemTypeEnum.ASSIGNMENT,
            completed_at=submission.submitted_at,  # Use submission time
            meta_data={
                "submission_id": str(submission.id),
                "status": "submitted",
            },  # Store link
        )
        crud_roadmap.create_user_progress(db=db, progress_in=progress_in)

        # 4. Award Partial Points for Submission
        # Example: Award 25% of points just for submitting
        submission_points = int(assignment.points_reward * 0.25)
        if submission_points > 0:
            gamification_service.award_points(
                db=db,
                user=user,
                points_to_add=submission_points,
                reason=f"Assignment submitted: {assignment.title}",
            )

        # 5. Update Daily Streak
        gamification_service.update_daily_streak(db=db, user=user)

        return submission

    except ValueError as ve:  # Catch specific expected errors
        logger.warning(f"Value error during assignment submission: {ve}")
        raise  # Re-raise for the endpoint to handle (e.g., return 404)
    except Exception as e:
        logger.error(
            f"Error submitting assignment {assignment_id} for user {user.id}: {e}",
            exc_info=True,
        )
        return None


def grade_assignment(
    db: Session,
    submission_id: uuid.UUID,
    status: str,
    grade: Optional[float],
    feedback: Optional[str],
) -> Optional[crud_roadmap.UserAssignmentSubmission]:
    """
    Updates an assignment submission with grading information (status, grade, feedback).
    Awards remaining points if the status is 'passed'.
    Checks for related badges.
    Returns the updated UserAssignmentSubmission record or None on error.
    """
    logger.info(
        f"Grading assignment submission {submission_id}. Status: {status}, Grade: {grade}"
    )
    try:
        # 1. Fetch the submission
        submission = crud_roadmap.get_assignment_submission(
            db, submission_id=submission_id
        )
        if not submission:
            logger.error(
                f"Assignment submission {submission_id} not found for grading."
            )
            raise ValueError("Submission not found")

        # Optional: Prevent re-grading?
        # if submission.status != 'submitted':
        #     logger.warning(f"Attempting to re-grade submission {submission_id} which has status '{submission.status}'.")
        #     # Decide whether to allow or raise error

        # 2. Update the submission record
        update_in = crud_roadmap.UserAssignmentSubmissionUpdate(
            status=status, grade=grade, feedback=feedback
        )
        updated_submission = crud_roadmap.update_assignment_submission(
            db=db, db_submission=submission, update_in=update_in
        )

        # 3. Update corresponding UserProgress metadata
        progress = crud_roadmap.get_user_progress_for_item(
            db,
            user_id=updated_submission.user_id,
            item_id=updated_submission.assignment_id,
            item_type=ItemTypeEnum.ASSIGNMENT,
        )
        if progress:
            progress.meta_data = progress.meta_data or {}  # Ensure meta_data exists
            progress.meta_data.update({"status": status, "grade": grade})
            db.add(progress)
        else:
            logger.warning(
                f"Could not find UserProgress record for graded assignment {updated_submission.assignment_id}, user {updated_submission.user_id}."
            )

        # 4. Award Points if Passed
        if status == "passed":
            # Fetch user and original assignment for awarding points/badges
            user = crud_user.get_user(db, updated_submission.user_id)
            assignment = crud_roadmap.get_assignment(
                db, updated_submission.assignment_id
            )

            if user and assignment:
                # Calculate remaining points (assuming 25% awarded on submission)
                # Adjust logic based on your exact awarding strategy
                submission_points = int(assignment.points_reward * 0.25)
                passing_points = assignment.points_reward - submission_points

                # Optional: Bonus points for high grade
                if (
                    grade is not None and grade >= 0.9
                ):  # Example: 90% or higher gets bonus
                    passing_points += int(assignment.points_reward * 0.1)  # 10% bonus

                if passing_points > 0:
                    gamification_service.award_points(
                        db=db,
                        user=user,
                        points_to_add=passing_points,
                        reason=f"Assignment passed: {assignment.title}",
                    )

                # 5. Check for Badges
                gamification_service.check_and_award_badge(
                    db=db, user=user, badge_name="Assignment Complete"
                )
                if grade == 1.0:  # Perfect grade badge
                    gamification_service.check_and_award_badge(
                        db=db, user=user, badge_name="Top Marks"
                    )
            else:
                logger.error(
                    f"Could not award points/badges for submission {submission_id}: User or Assignment not found."
                )

        return updated_submission

    except ValueError as ve:
        logger.warning(f"Value error during assignment grading: {ve}")
        raise  # Re-raise for endpoint
    except Exception as e:
        logger.error(
            f"Error grading assignment submission {submission_id}: {e}", exc_info=True
        )
        return None
