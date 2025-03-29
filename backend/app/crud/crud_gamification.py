# app/crud/crud_gamification.py

import uuid
from typing import List, Optional, Sequence

# Import models related to gamification definitions and User for leaderboard
from app.models.user_models import Badge, User, UserLevel

# Import schemas used for managing definitions and the leaderboard response
from app.schemas.gamification_schemas import (
    BadgeCreate,
    BadgeUpdate,
    LeaderboardEntry,
    UserLevelCreate,
    UserLevelUpdate,
)

# Import SQLAlchemy specific features if needed for complex queries/loading
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

# --- UserLevel Definition CRUD (for Admin management) ---


def get_level(db: Session, level_id: uuid.UUID) -> Optional[UserLevel]:
    return db.get(UserLevel, level_id)


def get_level_by_name(db: Session, name: str) -> Optional[UserLevel]:
    statement = select(UserLevel).where(UserLevel.name == name)
    return db.exec(statement).first()


def get_levels(db: Session, skip: int = 0, limit: int = 100) -> Sequence[UserLevel]:
    statement = (
        select(UserLevel).order_by(UserLevel.min_points).offset(skip).limit(limit)
    )
    return db.exec(statement).all()


def create_level(db: Session, *, level_in: UserLevelCreate) -> UserLevel:
    db_level = UserLevel.model_validate(level_in)
    db.add(db_level)
    return db_level


def update_level(
    db: Session, *, db_level: UserLevel, level_in: UserLevelUpdate
) -> UserLevel:
    update_data = level_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_level, key, value)
    db.add(db_level)
    return db_level


def delete_level(db: Session, level_id: uuid.UUID) -> Optional[UserLevel]:
    db_level = db.get(UserLevel, level_id)
    if db_level:
        db.delete(db_level)
    return db_level


def get_badge(db: Session, badge_id: uuid.UUID) -> Optional[Badge]:
    return db.get(Badge, badge_id)


def get_badge_by_name(db: Session, name: str) -> Optional[Badge]:
    statement = select(Badge).where(Badge.name == name)
    return db.exec(statement).first()


def get_badges(
    db: Session, skip: int = 0, limit: int = 100, category: Optional[str] = None
) -> Sequence[Badge]:
    statement = select(Badge)
    if category:
        statement = statement.where(Badge.category == category)
    statement = statement.order_by(Badge.category, Badge.name).offset(skip).limit(limit)
    return db.exec(statement).all()


def create_badge(db: Session, *, badge_in: BadgeCreate) -> Badge:
    db_badge = Badge.model_validate(badge_in)
    db.add(db_badge)
    return db_badge


def update_badge(db: Session, *, db_badge: Badge, badge_in: BadgeUpdate) -> Badge:
    update_data = badge_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_badge, key, value)
    db.add(db_badge)
    return db_badge


def delete_badge(db: Session, badge_id: uuid.UUID) -> Optional[Badge]:
    db_badge = db.get(Badge, badge_id)
    if db_badge:
        db.delete(db_badge)
    return db_badge


def get_leaderboard(db: Session, limit: int = 10) -> List[LeaderboardEntry]:
    statement = (
        select(User)
        .options(selectinload(User.level))
        .where(User.is_active is True)
        .order_by(User.points.desc(), User.created_at.asc())
        .limit(limit)
    )
    top_users = db.exec(statement).all()

    leaderboard = [
        LeaderboardEntry(
            rank=idx + 1,
            user_id=user.id,
            username=user.username,
            points=user.points,
            level_name=user.level.name if user.level else "Unranked",
        )
        for idx, user in enumerate(top_users)
    ]
    return leaderboard
