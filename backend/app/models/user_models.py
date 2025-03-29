import uuid
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .roadmap_models import UserAssignmentSubmission, UserProgress, UserQuizAttempt


class UserLevelBase(SQLModel):
    name: str = Field(index=True, unique=True)
    min_points: int = Field(index=True)


class UserLevel(UserLevelBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    users: List["User"] = Relationship(back_populates="level")


class BadgeBase(SQLModel):
    name: str = Field(index=True, unique=True)
    description: str
    category: str = Field(index=True)
    icon_url: Optional[str] = None


class Badge(BadgeBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_links: List["UserBadgeLink"] = Relationship(back_populates="badge")


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    username: Optional[str] = Field(
        default=None, unique=True, index=True, nullable=True
    )
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    supabase_auth_id: uuid.UUID = Field(unique=True, index=True)
    hashed_password: Optional[str] = Field(default=None, nullable=True)
    points: int = Field(default=0, index=True)
    level_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="userlevel.id", nullable=True
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    level: Optional[UserLevel] = Relationship(back_populates="users")
    badges: List["UserBadgeLink"] = Relationship(back_populates="user")
    streaks: Optional["UserStreak"] = Relationship(back_populates="user")
    progress: List["UserProgress"] = Relationship(back_populates="user")
    quiz_attempts: List["UserQuizAttempt"] = Relationship(back_populates="user")
    assignment_submissions: List["UserAssignmentSubmission"] = Relationship(
        back_populates="user"
    )


class UserBadgeLink(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    badge_id: uuid.UUID = Field(foreign_key="badge.id", index=True)
    awarded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: "User" = Relationship(back_populates="badges")
    badge: Badge = Relationship(back_populates="user_links")


class UserStreak(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    current_streak: int = Field(default=0)
    longest_streak: int = Field(default=0)
    last_completed_date: Optional[date] = Field(default=None)

    user: User = Relationship(back_populates="streaks")


if TYPE_CHECKING:
    from .roadmap_models import UserAssignmentSubmission, UserProgress, UserQuizAttempt
