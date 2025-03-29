import uuid
from datetime import datetime
from typing import List, Optional

from app.models.user_models import User, UserBadgeLink, UserStreak
from app.schemas.user_schemas import UserCreateInternal, UserUpdate
from sqlmodel import Session, select


def get_user(db: Session, user_id: uuid.UUID) -> Optional[User]:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    return db.exec(statement).first()


def get_user_by_supabase_id(db: Session, supabase_auth_id: uuid.UUID) -> Optional[User]:
    statement = select(User).where(User.supabase_auth_id == supabase_auth_id)
    return db.exec(statement).first()


# Optional: Keep if usernames are actively used and need lookup
# def get_user_by_username(db: Session, username: str) -> Optional[User]:
#     """Gets a user by their username (if used)."""
#     statement = select(User).where(User.username == username)
#     return db.exec(statement).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    statement = select(User).offset(skip).limit(limit).order_by(User.created_at)
    return db.exec(statement).all()


def create_user_from_supabase(db: Session, *, user_in: UserCreateInternal) -> User:
    db_user = User.model_validate(user_in)
    db.add(db_user)
    return db_user


def update_user(db: Session, *, db_user: User, user_in: UserUpdate) -> User:
    user_data = user_in.model_dump(exclude_unset=True)
    needs_update = False
    for key, value in user_data.items():
        if getattr(db_user, key) != value:
            setattr(db_user, key, value)
            needs_update = True

    if needs_update:
        db_user.updated_at = datetime.utcnow()
        db.add(db_user)
    return db_user


def is_user_active(user: User) -> bool:
    return user.is_active


def add_badge_to_user(
    db: Session, *, user_id: uuid.UUID, badge_id: uuid.UUID
) -> UserBadgeLink:
    link = UserBadgeLink(user_id=user_id, badge_id=badge_id)
    db.add(link)
    return link


def get_user_badges(db: Session, *, user_id: uuid.UUID) -> List[UserBadgeLink]:
    from sqlalchemy.orm import selectinload

    statement = (
        select(UserBadgeLink)
        .options(selectinload(UserBadgeLink.badge))
        .where(UserBadgeLink.user_id == user_id)
        .order_by(UserBadgeLink.awarded_at.desc())
    )
    return db.exec(statement).all()


def get_or_create_user_streak(db: Session, *, user_id: uuid.UUID) -> UserStreak:
    streak = db.get(UserStreak, user_id)
    if not streak:
        streak = UserStreak(user_id=user_id)
        db.add(streak)
    return streak


def update_user_streak(db: Session, *, db_streak: UserStreak, **kwargs) -> UserStreak:
    for key, value in kwargs.items():
        setattr(db_streak, key, value)
    db.add(db_streak)
    return db_streak
