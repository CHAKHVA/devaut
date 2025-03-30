from datetime import datetime

from sqlmodel import SQLModel

from app.models.quiz_models import DifficultyLevel, QuestionType


class JobDescriptionBase(SQLModel):
    original_text: str


class AnswerBase(SQLModel):
    text: str
    is_correct: bool = False


class QuestionBase(SQLModel):
    text: str
    question_type: QuestionType = QuestionType.SINGLE_CHOICE
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM


class QuizBase(SQLModel):
    title: str
    description: str | None = None
    difficulty: DifficultyLevel
    time_limit_seconds: int
    tags: list[str] | None = None


class QuizReadMinimal(SQLModel):
    id: int
    title: str
    difficulty: DifficultyLevel
    created_at: datetime


class JobDescriptionReadMinimal(SQLModel):
    id: int
    created_at: datetime
    original_text: str | None = None


class JobDescriptionCreate(JobDescriptionBase):
    pass


class AnswerCreate(AnswerBase):
    pass


class QuestionCreate(QuestionBase):
    answers: list[AnswerCreate] | None = None


class AnswerRead(AnswerBase):
    id: int
    created_at: datetime


class QuestionRead(QuestionBase):
    id: int
    created_at: datetime
    answers: list[AnswerRead] = []


class QuizRead(QuizBase):
    id: int
    created_at: datetime
    updated_at: datetime
    source_jd: JobDescriptionReadMinimal | None = None
    questions: list[QuestionRead] = []


class JobDescriptionRead(JobDescriptionBase):
    id: int
    created_at: datetime
    generated_quiz: QuizReadMinimal | None = None


class GenerateQuizRequest(SQLModel):
    job_description_text: str
    # desired_difficulty: DifficultyLevel | None = None


class GenerateQuizResponse(SQLModel):
    job_description: JobDescriptionRead
    # quiz: QuizRead


class MatchQuizRequest(SQLModel):
    job_description_text: str | None = None
    tags: list[str] | None = None


class MatchedQuizInfo(QuizReadMinimal):
    match_score: float
    tags: list[str] | None = None
    description: str | None = None


class MatchQuizResponse(SQLModel):
    matched_quizzes: list[MatchedQuizInfo] = []
