import uuid
from typing import Optional

from app.models.user_models import BadgeBase, UserLevelBase
from sqlmodel import Field, SQLModel


class UserLevelCreate(UserLevelBase):
    pass


class UserLevelRead(UserLevelBase):
    id: uuid.UUID


class UserLevelUpdate(SQLModel):
    name: Optional[str] = None
    min_points: Optional[int] = None


class BadgeCreate(BadgeBase):
    pass


class BadgeRead(BadgeBase):
    id: uuid.UUID


class BadgeUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    icon_url: Optional[str] = None


class LeaderboardEntry(SQLModel):
    rank: int
    user_id: uuid.UUID
    username: Optional[str]
    points: int
    level_name: Optional[str] = Field(
        default="Unranked", description="Name of the user's current level"
    )
