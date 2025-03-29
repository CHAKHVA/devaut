import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.models.roadmap_models import ItemTypeEnum
from pydantic import HttpUrl
from sqlmodel import Field, SQLModel


class LearningResourceBaseSchema(SQLModel):
    title: str
    type: str
    url: Optional[HttpUrl | str] = None
    content: Optional[str] = None
    order: Optional[int] = 0
    estimated_time_minutes: Optional[int] = None


class LearningResourceCreate(LearningResourceBaseSchema):
    pass


class LearningResourceRead(LearningResourceBaseSchema):
    id: uuid.UUID
    module_id: uuid.UUID
    created_at: datetime


class LearningResourceUpdate(SQLModel):
    title: Optional[str] = None
    type: Optional[str] = None
    url: Optional[HttpUrl | str] = None
    content: Optional[str] = None
    order: Optional[int] = None
    estimated_time_minutes: Optional[int] = None


class AssignmentBaseSchema(SQLModel):
    title: str
    description: str
    points_reward: Optional[int] = 10


class AssignmentCreate(AssignmentBaseSchema):
    pass


class AssignmentRead(AssignmentBaseSchema):
    id: uuid.UUID
    module_id: uuid.UUID
    created_at: datetime


class AssignmentUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    points_reward: Optional[int] = None


class QuizQuestionBaseSchema(SQLModel):
    question_text: str
    options: Dict[str, Any]
    correct_option_keys: List[str]
    ai_hint: Optional[str] = None
    order: Optional[int] = 0


class QuizQuestionCreate(QuizQuestionBaseSchema):
    pass


class QuizQuestionRead(QuizQuestionBaseSchema):
    id: uuid.UUID
    quiz_id: uuid.UUID
    created_at: datetime


class QuizQuestionUpdate(SQLModel):
    question_text: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    correct_option_keys: Optional[List[str]] = None
    ai_hint: Optional[str] = None
    order: Optional[int] = None


class QuizBaseSchema(SQLModel):
    title: str
    points_reward: Optional[int] = 5


class QuizCreate(QuizBaseSchema):
    questions: Optional[List[QuizQuestionCreate]] = []


class QuizRead(QuizBaseSchema):
    id: uuid.UUID
    module_id: uuid.UUID
    created_at: datetime
    questions: List[QuizQuestionRead] = []


class QuizUpdate(SQLModel):
    title: Optional[str] = None
    points_reward: Optional[int] = None


class RoadmapModuleBaseSchema(SQLModel):
    title: str
    order: Optional[int] = 0


class RoadmapModuleCreate(RoadmapModuleBaseSchema):
    learning_resources: Optional[List[LearningResourceCreate]] = []
    assignments: Optional[List[AssignmentCreate]] = []
    quizzes: Optional[List[QuizCreate]] = []


class RoadmapModuleRead(RoadmapModuleBaseSchema):
    id: uuid.UUID
    roadmap_id: uuid.UUID
    created_at: datetime
    learning_resources: List[LearningResourceRead] = []
    assignments: List[AssignmentRead] = []
    quizzes: List[QuizRead] = []


class RoadmapModuleUpdate(SQLModel):
    title: Optional[str] = None
    order: Optional[int] = None


class RoadmapBaseSchema(SQLModel):
    title: str
    description: str
    topic: str
    is_active: Optional[bool] = True


class RoadmapCreate(RoadmapBaseSchema):
    modules: Optional[List[RoadmapModuleCreate]] = []


class RoadmapRead(RoadmapBaseSchema):
    id: uuid.UUID
    created_at: datetime


class RoadmapReadWithDetails(RoadmapRead):
    modules: List[RoadmapModuleRead] = []


class RoadmapUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    topic: Optional[str] = None
    is_active: Optional[bool] = None


class UserProgressBase(SQLModel):
    item_id: uuid.UUID
    item_type: ItemTypeEnum


class UserProgressCreate(UserProgressBase):
    user_id: uuid.UUID
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    meta_data: Optional[Dict[str, Any]] = None


class UserProgressRead(UserProgressBase):
    id: uuid.UUID
    user_id: uuid.UUID
    completed_at: Optional[datetime]
    meta_data: Optional[Dict[str, Any]]


class UserQuizAttemptBase(SQLModel):
    quiz_id: uuid.UUID


class UserQuizAttemptCreate(UserQuizAttemptBase):
    answers: Dict[str, List[str]]


class UserQuizAttemptRead(UserQuizAttemptBase):
    id: uuid.UUID
    user_id: uuid.UUID
    score: float
    answers: Dict[str, List[str]]
    passed: bool
    started_at: datetime
    completed_at: Optional[datetime]


class UserAssignmentSubmissionBase(SQLModel):
    assignment_id: uuid.UUID


class UserAssignmentSubmissionCreate(UserAssignmentSubmissionBase):
    submission_content: str


class UserAssignmentSubmissionRead(UserAssignmentSubmissionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    submitted_at: datetime
    submission_content: Optional[str]
    status: str
    grade: Optional[float]
    feedback: Optional[str]
    graded_at: Optional[datetime]


class UserAssignmentSubmissionUpdate(SQLModel):
    status: Optional[str] = None
    grade: Optional[float] = None
    feedback: Optional[str] = None
