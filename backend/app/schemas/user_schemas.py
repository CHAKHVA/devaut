import uuid
from datetime import date, datetime
from typing import List, Optional

from app.models.user_models import BadgeBase, UserLevelBase
from pydantic import EmailStr
from sqlmodel import SQLModel


class UserLevelRead(UserLevelBase):
    id: uuid.UUID


class BadgeRead(BadgeBase):
    id: uuid.UUID


class UserBadgeRead(SQLModel):
    badge: BadgeRead
    awarded_at: datetime


class UserStreakRead(SQLModel):
    user_id: uuid.UUID
    current_streak: int
    longest_streak: int
    last_completed_date: Optional[date]


class UserBaseSchema(SQLModel):
    email: EmailStr
    username: Optional[str] = None
    is_active: Optional[bool] = True


class UserCreateInternal(UserBaseSchema):
    supabase_auth_id: uuid.UUID


class UserUpdate(SQLModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDBBase(UserBaseSchema):
    id: uuid.UUID
    supabase_auth_id: uuid.UUID
    points: int
    level_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserRead(UserBaseSchema):
    id: uuid.UUID
    points: int
    level: Optional[UserLevelRead] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserReadMe(UserRead):
    email: EmailStr
    badges: List[UserBadgeRead] = []
    streak: Optional[UserStreakRead] = None
