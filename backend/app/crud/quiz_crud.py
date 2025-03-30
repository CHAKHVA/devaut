from typing import List, Optional, Sequence

from sqlmodel import Session, select

from app.models.quiz_models import (
    Answer,
    DifficultyLevel,
    JobDescription,
    Question,
    Quiz,
)
from app.schemas.quiz_schemas import JobDescriptionCreate, QuestionCreate


def create_job_description(
    db: Session, *, jd_in: JobDescriptionCreate
) -> JobDescription:
    db_jd = JobDescription.model_validate(jd_in)
    db.add(db_jd)
    db.commit()
    db.refresh(db_jd)
    return db_jd


def get_job_description(db: Session, jd_id: int) -> JobDescription | None:
    return db.get(JobDescription, jd_id)


def get_job_descriptions(
    db: Session, skip: int = 0, limit: int = 100
) -> Sequence[JobDescription]:
    statement = select(JobDescription).offset(skip).limit(limit)
    result = db.exec(statement)
    return result.all()


def create_quiz_linked_to_jd(
    db: Session,
    *,
    source_jd: JobDescription,
    title: str,
    difficulty: DifficultyLevel,
    time_limit_seconds: int,
    tags: Optional[List[str]],
    questions: List[Question],
    description: Optional[str] = None,
) -> Quiz:
    if source_jd.generated_quiz is not None:
        raise ValueError(
            f"Job Description {source_jd.id} already has a generated quiz."
        )

    db_quiz = Quiz(
        title=title,
        description=description,
        difficulty=difficulty,
        time_limit_seconds=time_limit_seconds,
        tags=tags,
        source_jd_id=source_jd.id,  # Link by ID
        questions=questions,
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    # db.refresh(source_jd) # uncomment if you directly return or use source_jd afterwards
    return db_quiz


def get_quiz(db: Session, quiz_id: int) -> Quiz | None:
    return db.get(Quiz, quiz_id)


def get_quiz_by_jd_id(db: Session, jd_id: int) -> Quiz | None:
    statement = select(Quiz).where(Quiz.source_jd_id == jd_id)
    result = db.exec(statement)
    return result.first()


def get_quizzes(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Quiz]:
    statement = select(Quiz).offset(skip).limit(limit)
    result = db.exec(statement)
    return result.all()


def get_quizzes_by_tags(
    db: Session, tags_to_match: List[str], require_all: bool = False, limit: int = 50
) -> Sequence[Quiz]:
    statement = select(Quiz)
    if tags_to_match:
        from sqlalchemy.dialects.postgresql import JSONB

        if require_all:
            statement = statement.where(
                Quiz.tags.astext.cast(JSONB).contains(tags_to_match)
            )
        else:
            statement = statement.where(
                Quiz.tags.astext.cast(JSONB).overlap(tags_to_match)
            )
            pass

    statement = statement.limit(limit)
    results = db.exec(statement)
    return results.all()


def create_question(db: Session, *, question_in: QuestionCreate) -> Question:
    answers_data = question_in.answers or []
    question_data = question_in.model_dump(exclude={"answers"})

    db_question = Question(**question_data)

    db_answers = []
    for answer_data in answers_data:
        db_answer = Answer.model_validate(answer_data)
        db_answer.question = db_question
        db_answers.append(db_answer)
        db.add(db_answer)

    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    # for ans in db_answers:
    #     db.refresh(ans)
    return db_question


def get_question(db: Session, question_id: int) -> Question | None:
    return db.get(Question, question_id)


def get_questions(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Question]:
    statement = select(Question).offset(skip).limit(limit)
    result = db.exec(statement)
    return result.all()


def get_questions_by_ids(db: Session, question_ids: List[int]) -> Sequence[Question]:
    if not question_ids:
        return []
    statement = select(Question).where(Question.id.in_(question_ids))
    result = db.exec(statement)
    return result.all()


def get_answer(db: Session, answer_id: int) -> Answer | None:
    return db.get(Answer, answer_id)
