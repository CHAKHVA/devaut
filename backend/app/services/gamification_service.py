# app/services/gamification_service.py

import logging
import uuid
from datetime import date, datetime, timedelta

# Import CRUD operations required by this service
from app.crud import (  # crud_gamification for getting level/badge defs
    crud_gamification,
    crud_user,
)

# Import necessary models
from app.models.user_models import Badge, User, UserBadgeLink, UserLevel, UserStreak
from sqlmodel import Session, select

logger = logging.getLogger(__name__)

# --- Point & Level Management ---


def award_points(
    db: Session, user: User, points_to_add: int, reason: str = "Activity completion"
) -> User:
    """
    Adds points to a user's score, logs the action, and checks for level up.
    Returns the updated User object (changes still need to be committed by caller context).
    """
    if points_to_add <= 0:
        return user  # No change for zero or negative points

    user.points += points_to_add
    logger.info(
        f"Awarding {points_to_add} points to user {user.id} for '{reason}'. New total: {user.points}"
    )

    # Check if the user qualifies for a higher level
    current_level_points = user.level.min_points if user.level else -1

    # Find the highest level definition the user meets or exceeds
    # Note: Assumes UserLevel table is populated with levels ordered by min_points implicitly or explicitly
    eligible_level = crud_gamification.get_level_by_points(
        db, user.points
    )  # Assumes get_level_by_points exists

    # If get_level_by_points doesn't exist, use this logic:
    # statement = select(UserLevel).where(UserLevel.min_points <= user.points).order_by(UserLevel.min_points.desc())
    # eligible_level = db.exec(statement).first()

    if eligible_level and (user.level_id != eligible_level.id):
        # Check if the new eligible level is different and higher than the current one
        if user.level is None or eligible_level.min_points > user.level.min_points:
            logger.info(f"User {user.id} leveled up to '{eligible_level.name}'!")
            user.level_id = eligible_level.id
            user.level = (
                eligible_level  # Update the relationship proxy for immediate use
            )
            # Optionally: Award a specific badge for leveling up
            # check_and_award_badge(db, user, f"Level {eligible_level.name} Achieved")

    db.add(user)  # Mark the user object as changed in the session
    return user


# Helper for the above - add to crud_gamification.py if preferred
def get_level_by_points(db: Session, points: int) -> Optional[UserLevel]:
    """Finds the highest level definition that a user qualifies for based on points."""
    statement = (
        select(UserLevel)
        .where(UserLevel.min_points <= points)
        .order_by(UserLevel.min_points.desc())
    )  # type: ignore
    return db.exec(statement).first()


# --- Badge Management ---


def check_and_award_badge(
    db: Session, user: User, badge_name: str, check_existing: bool = True
) -> Optional[UserBadgeLink]:
    """
    Checks if a user should be awarded a specific badge by name.
    If `check_existing` is True, it first checks if the user already has the badge.
    Awards the badge if applicable and returns the UserBadgeLink record.
    Returns None if the badge doesn't exist, the user already has it (and check_existing=True), or an error occurs.
    """
    # 1. Check if user already has the badge (optional)
    if check_existing:
        # Optimize this check if performance becomes an issue (e.g., query DB directly)
        has_badge = any(link.badge.name == badge_name for link in user.badges)
        if has_badge:
            # logger.debug(f"User {user.id} already has badge '{badge_name}'. Skipping award.")
            return None  # Already awarded

    # 2. Find the badge definition in the database
    badge_to_award = crud_gamification.get_badge_by_name(db, name=badge_name)

    if not badge_to_award:
        logger.warning(f"Attempted to award non-existent badge named '{badge_name}'.")
        return None

    # 3. Award the badge by creating the link record
    try:
        link = crud_user.add_badge_to_user(
            db=db, user_id=user.id, badge_id=badge_to_award.id
        )
        logger.info(
            f"Awarded badge '{badge_name}' (ID: {badge_to_award.id}) to user {user.id}"
        )
        # Optionally award points for earning a badge
        # award_points(db, user, points=5, reason=f"Badge Earned: {badge_name}")
        return link
    except Exception as e:
        logger.error(f"Error awarding badge '{badge_name}' to user {user.id}: {e}")
        # Consider rolling back if this service managed its own transaction, but rely on get_db wrapper for now.
        return None


# --- Streak Management ---


def update_daily_streak(db: Session, user: User) -> Optional[UserStreak]:
    """
    Updates the user's daily activity streak based on today's date.
    Should be called once per day when the user completes their first qualifying activity.
    Awards bonus points for continuing a streak.
    Returns the updated UserStreak object.
    """
    today = date.today()
    try:
        # Get or create the streak record for the user
        streak_data = crud_user.get_or_create_user_streak(db=db, user_id=user.id)

        last_completed = streak_data.last_completed_date

        # If already updated today, do nothing
        if last_completed == today:
            # logger.debug(f"Streak already updated today for user {user.id}")
            return streak_data

        yesterday = today - timedelta(days=1)
        current_streak = streak_data.current_streak
        bonus_points = 0

        if last_completed == yesterday:
            # Streak continued
            current_streak += 1
            logger.info(f"User {user.id} continued streak. Current: {current_streak}")
            # Award bonus points (e.g., 1 point per day in streak, capped maybe?)
            bonus_points = min(
                current_streak, 5
            )  # Example: 1 point per day, max 5 bonus points
            reason = f"Daily streak bonus day {current_streak}"
        else:
            # Streak broken or first activity
            logger.info(f"User {user.id} started/reset streak. Current: 1")
            current_streak = 1
            bonus_points = 1  # Award 1 point for starting/doing activity
            reason = "Daily activity completed"

        # Update streak record fields
        streak_data.last_completed_date = today
        streak_data.current_streak = current_streak
        streak_data.longest_streak = max(streak_data.longest_streak, current_streak)

        # Mark streak_data as changed in the session
        db.add(streak_data)

        # Award points related to the streak update
        if bonus_points > 0:
            award_points(db=db, user=user, points_to_add=bonus_points, reason=reason)
            # Note: award_points also adds 'user' to the session

        return streak_data

    except Exception as e:
        logger.error(f"Error updating streak for user {user.id}: {e}")
        return None
