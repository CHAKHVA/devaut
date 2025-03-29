import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlmodel import JSON, Column, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user_models import User


class ItemTypeEnum(str, Enum):
    MODULE = "module"
    RESOURCE = "resource"
    ASSIGNMENT = "assignment"
    QUIZ = "quiz"


class RoadmapBase(SQLModel):
    title: str = Field(index=True)
    description: str
    topic: str = Field(index=True)
    is_active: bool = Field(default=True)
    # creator_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")


class Roadmap(RoadmapBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    modules: List["RoadmapModule"] = Relationship(back_populates="roadmap")
    # creator: Optional["User"] = Relationship(back_populates="roadmaps_created")


class RoadmapModuleBase(SQLModel):
    title: str
    order: int = Field(default=0, index=True)


class RoadmapModule(RoadmapModuleBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    roadmap_id: uuid.UUID = Field(foreign_key="roadmap.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    roadmap: Roadmap = Relationship(back_populates="modules")
    learning_resources: List["LearningResource"] = Relationship(back_populates="module")
    assignments: List["Assignment"] = Relationship(back_populates="module")
    quizzes: List["Quiz"] = Relationship(back_populates="module")


class LearningResourceBase(SQLModel):
    title: str
    type: str = Field(index=True)
    url: Optional[str] = None
    content: Optional[str] = None
    order: int = Field(default=0, index=True)
    estimated_time_minutes: Optional[int] = None


class LearningResource(LearningResourceBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    module_id: uuid.UUID = Field(foreign_key="roadmapmodule.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    module: RoadmapModule = Relationship(back_populates="learning_resources")


class AssignmentBase(SQLModel):
    title: str
    description: str
    points_reward: int = Field(default=10)


class Assignment(AssignmentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    module_id: uuid.UUID = Field(foreign_key="roadmapmodule.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    module: RoadmapModule = Relationship(back_populates="assignments")
    submissions: List["UserAssignmentSubmission"] = Relationship(
        back_populates="assignment"
    )


class QuizBase(SQLModel):
    title: str
    points_reward: int = Field(default=5)


class Quiz(QuizBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    module_id: uuid.UUID = Field(foreign_key="roadmapmodule.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    module: RoadmapModule = Relationship(back_populates="quizzes")
    questions: List["QuizQuestion"] = Relationship(back_populates="quiz")
    attempts: List["UserQuizAttempt"] = Relationship(back_populates="quiz")


class QuizQuestionBase(SQLModel):
    question_text: str
    options: Dict[str, Any] = Field(sa_column=Column(JSON))
    correct_option_keys: List[str] = Field(sa_column=Column(JSON))
    ai_hint: Optional[str] = None
    order: int = Field(default=0, index=True)


class QuizQuestion(QuizQuestionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    quiz_id: uuid.UUID = Field(foreign_key="quiz.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    quiz: Quiz = Relationship(back_populates="questions")


class UserProgress(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    item_id: uuid.UUID = Field(index=True)
    item_type: ItemTypeEnum = Field(index=True)
    completed_at: Optional[datetime] = Field(default=None, index=True)
    meta_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    user: "User" = Relationship(back_populates="progress")


class UserQuizAttempt(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    quiz_id: uuid.UUID = Field(foreign_key="quiz.id", index=True)
    score: float
    answers: Dict[str, List[str]] = Field(sa_column=Column(JSON))
    passed: bool = Field(default=False)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = Field(default=None)

    user: "User" = Relationship(back_populates="quiz_attempts")
    quiz: Quiz = Relationship(back_populates="attempts")


class UserAssignmentSubmission(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    assignment_id: uuid.UUID = Field(foreign_key="assignment.id", index=True)
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    submission_content: Optional[str] = None
    status: str = Field(default="submitted", index=True)
    grade: Optional[float] = None
    feedback: Optional[str] = None
    graded_at: Optional[datetime] = None

    user: "User" = Relationship(back_populates="assignment_submissions")
    assignment: Assignment = Relationship(back_populates="submissions")
