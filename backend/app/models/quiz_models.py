import enum
from datetime import datetime, timezone

from sqlmodel import JSON, Column, Field, Relationship, SQLModel


class QuestionType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_CHOICE = "single_choice"


class DifficultyLevel(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuizQuestionLink(SQLModel, table=True):
    quiz_id: int | None = Field(default=None, foreign_key="quiz.id", primary_key=True)
    question_id: int | None = Field(
        default=None, foreign_key="question.id", primary_key=True
    )


class JobDescription(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    original_text: str = Field(nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    generated_quiz: "Quiz" = Relationship(back_populates="source_jd")


class Question(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
    question_type: QuestionType = Field(default=QuestionType.SINGLE_CHOICE)
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM)
    created_at: datetime = Field(
        default_factory=datetime.now(timezone.utc), nullable=False
    )

    answers: list["Answer"] = Relationship(back_populates="question")
    quizzes: list["Quiz"] = Relationship(
        back_populates="questions", link_model=QuizQuestionLink
    )


class Answer(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    question_id: int = Field(foreign_key="question.id")
    text: str
    is_correct: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=datetime.now(timezone.utc), nullable=False
    )

    question: "Question" = Relationship(back_populates="answers")


class Quiz(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = None
    difficulty: DifficultyLevel = Field(nullable=False)
    time_limit_seconds: int = Field(nullable=False)
    tags: list[str] | None = Field(default=None, sa_column=Column(JSON))

    created_at: datetime = Field(
        default_factory=datetime.now(timezone.utc), nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.now(timezone.utc), nullable=False
    )
    source_jd_id: int | None = Field(
        default=None, foreign_key="jobdescription.id", nullable=True, unique=True
    )

    source_jd: "JobDescription" = Relationship(back_populates="generated_quiz")
    questions: list["Question"] = Relationship(
        back_populates="quizzes", link_model=QuizQuestionLink
    )
