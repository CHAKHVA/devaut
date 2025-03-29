import uuid
from datetime import datetime
from typing import Optional, Sequence

from app.models.roadmap_models import (
    Assignment,
    ItemTypeEnum,
    LearningResource,
    Quiz,
    QuizQuestion,
    Roadmap,
    RoadmapModule,
    UserAssignmentSubmission,
    UserProgress,
    UserQuizAttempt,
)
from app.schemas.roadmap_schemas import (
    AssignmentCreate,
    AssignmentUpdate,
    LearningResourceCreate,
    LearningResourceUpdate,
    QuizCreate,
    QuizQuestionCreate,
    QuizQuestionUpdate,
    QuizUpdate,
    RoadmapCreate,
    RoadmapModuleCreate,
    RoadmapModuleUpdate,
    RoadmapUpdate,
    UserAssignmentSubmissionCreate,
    UserAssignmentSubmissionUpdate,
    UserProgressCreate,
    UserQuizAttemptCreate,
)
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select


def create_roadmap(db: Session, *, roadmap_in: RoadmapCreate) -> Roadmap:
    modules_data = roadmap_in.modules or []
    roadmap_data = roadmap_in.model_dump(exclude={"modules"})
    db_roadmap = Roadmap(**roadmap_data)
    db.add(db_roadmap)
    db.flush()

    created_modules = []
    for module_in in modules_data:
        db_module = create_module_for_roadmap(
            db=db, module_in=module_in, roadmap_id=db_roadmap.id, roadmap_obj=db_roadmap
        )
        created_modules.append(db_module)

    return db_roadmap


def get_roadmap(db: Session, roadmap_id: uuid.UUID) -> Optional[Roadmap]:
    return db.get(Roadmap, roadmap_id)


def get_roadmap_with_details(db: Session, roadmap_id: uuid.UUID) -> Optional[Roadmap]:
    statement = (
        select(Roadmap)
        .options(
            selectinload(Roadmap.modules).selectinload(  # Load modules
                RoadmapModule.learning_resources
            ),  # Load resources within modules
            selectinload(Roadmap.modules).selectinload(
                RoadmapModule.assignments
            ),  # Load assignments within modules
            selectinload(Roadmap.modules)
            .selectinload(RoadmapModule.quizzes)  # Load quizzes within modules
            .selectinload(Quiz.questions),  # Load questions within quizzes
        )
        .where(Roadmap.id == roadmap_id)
    )
    result = db.exec(statement).first()
    return result


def get_roadmaps(
    db: Session, skip: int = 0, limit: int = 100, topic: Optional[str] = None
) -> Sequence[Roadmap]:
    statement = select(Roadmap)
    if topic:
        statement = statement.where(Roadmap.topic == topic)
    statement = statement.order_by(Roadmap.title).offset(skip).limit(limit)
    results = db.exec(statement).all()
    return results


def update_roadmap(
    db: Session, *, db_roadmap: Roadmap, roadmap_in: RoadmapUpdate
) -> Roadmap:
    update_data = roadmap_in.model_dump(exclude_unset=True)
    needs_update = False
    for key, value in update_data.items():
        if getattr(db_roadmap, key) != value:
            setattr(db_roadmap, key, value)
            needs_update = True
    db.add(db_roadmap)
    return db_roadmap


def delete_roadmap(db: Session, roadmap_id: uuid.UUID) -> Optional[Roadmap]:
    db_roadmap = db.get(Roadmap, roadmap_id)
    if db_roadmap:
        db.delete(db_roadmap)
    return db_roadmap


def create_module_for_roadmap(
    db: Session,
    *,
    module_in: RoadmapModuleCreate,
    roadmap_id: uuid.UUID,
    roadmap_obj: Optional[Roadmap] = None,
) -> RoadmapModule:
    resources_data = module_in.learning_resources or []
    assignments_data = module_in.assignments or []
    quizzes_data = module_in.quizzes or []
    module_base_data = module_in.model_dump(
        exclude={"learning_resources", "assignments", "quizzes"}
    )

    db_module = RoadmapModule(**module_base_data, roadmap_id=roadmap_id)
    if roadmap_obj:
        db_module.roadmap = roadmap_obj

    db.add(db_module)
    db.flush()

    for resource_in in resources_data:
        create_resource_for_module(
            db=db, resource_in=resource_in, module_id=db_module.id, module_obj=db_module
        )

    for assignment_in in assignments_data:
        create_assignment_for_module(
            db=db,
            assignment_in=assignment_in,
            module_id=db_module.id,
            module_obj=db_module,
        )

    for quiz_in in quizzes_data:
        create_quiz_for_module(
            db=db, quiz_in=quiz_in, module_id=db_module.id, module_obj=db_module
        )

    return db_module


def get_module(db: Session, module_id: uuid.UUID) -> Optional[RoadmapModule]:
    return db.get(RoadmapModule, module_id)


def get_modules_for_roadmap(
    db: Session, roadmap_id: uuid.UUID
) -> Sequence[RoadmapModule]:
    statement = (
        select(RoadmapModule)
        .where(RoadmapModule.roadmap_id == roadmap_id)
        .order_by(RoadmapModule.order)
    )
    results = db.exec(statement).all()
    return results


def update_module(
    db: Session, *, db_module: RoadmapModule, module_in: RoadmapModuleUpdate
) -> RoadmapModule:
    update_data = module_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_module, key, value)
    db.add(db_module)
    return db_module


def delete_module(db: Session, module_id: uuid.UUID) -> Optional[RoadmapModule]:
    db_module = db.get(RoadmapModule, module_id)
    if db_module:
        db.delete(db_module)
    return db_module


def create_resource_for_module(
    db: Session,
    *,
    resource_in: LearningResourceCreate,
    module_id: uuid.UUID,
    module_obj: Optional[RoadmapModule] = None,
) -> LearningResource:
    db_resource = LearningResource(**resource_in.model_dump(), module_id=module_id)
    if module_obj:
        db_resource.module = module_obj
    db.add(db_resource)
    return db_resource


def get_resource(db: Session, resource_id: uuid.UUID) -> Optional[LearningResource]:
    return db.get(LearningResource, resource_id)


def update_resource(
    db: Session, *, db_resource: LearningResource, resource_in: LearningResourceUpdate
) -> LearningResource:
    update_data = resource_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_resource, key, value)
    db.add(db_resource)
    return db_resource


def delete_resource(db: Session, resource_id: uuid.UUID) -> Optional[LearningResource]:
    db_resource = db.get(LearningResource, resource_id)
    if db_resource:
        db.delete(db_resource)
    return db_resource


def create_assignment_for_module(
    db: Session,
    *,
    assignment_in: AssignmentCreate,
    module_id: uuid.UUID,
    module_obj: Optional[RoadmapModule] = None,
) -> Assignment:
    db_assignment = Assignment(**assignment_in.model_dump(), module_id=module_id)
    if module_obj:
        db_assignment.module = module_obj
    db.add(db_assignment)
    return db_assignment


def get_assignment(db: Session, assignment_id: uuid.UUID) -> Optional[Assignment]:
    return db.get(Assignment, assignment_id)


def update_assignment(
    db: Session, *, db_assignment: Assignment, assignment_in: AssignmentUpdate
) -> Assignment:
    update_data = assignment_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_assignment, key, value)
    db.add(db_assignment)
    return db_assignment


def delete_assignment(db: Session, assignment_id: uuid.UUID) -> Optional[Assignment]:
    db_assignment = db.get(Assignment, assignment_id)
    if db_assignment:
        db.delete(db_assignment)
    return db_assignment


def create_quiz_for_module(
    db: Session,
    *,
    quiz_in: QuizCreate,
    module_id: uuid.UUID,
    module_obj: Optional[RoadmapModule] = None,
) -> Quiz:
    questions_data = quiz_in.questions or []
    quiz_base_data = quiz_in.model_dump(exclude={"questions"})

    db_quiz = Quiz(**quiz_base_data, module_id=module_id)
    if module_obj:
        db_quiz.module = module_obj

    db.add(db_quiz)
    db.flush()

    for question_in in questions_data:
        create_question_for_quiz(
            db=db, question_in=question_in, quiz_id=db_quiz.id, quiz_obj=db_quiz
        )

    return db_quiz


def get_quiz(db: Session, quiz_id: uuid.UUID) -> Optional[Quiz]:
    return db.get(Quiz, quiz_id)


def get_quiz_with_questions(db: Session, quiz_id: uuid.UUID) -> Optional[Quiz]:
    statement = (
        select(Quiz).options(selectinload(Quiz.questions)).where(Quiz.id == quiz_id)
    )
    result = db.exec(statement).first()
    return result


def update_quiz(db: Session, *, db_quiz: Quiz, quiz_in: QuizUpdate) -> Quiz:
    update_data = quiz_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_quiz, key, value)
    db.add(db_quiz)
    return db_quiz


def delete_quiz(db: Session, quiz_id: uuid.UUID) -> Optional[Quiz]:
    db_quiz = db.get(Quiz, quiz_id)
    if db_quiz:
        db.delete(db_quiz)
    return db_quiz


def create_question_for_quiz(
    db: Session,
    *,
    question_in: QuizQuestionCreate,
    quiz_id: uuid.UUID,
    quiz_obj: Optional[Quiz] = None,
) -> QuizQuestion:
    db_question = QuizQuestion(**question_in.model_dump(), quiz_id=quiz_id)
    if quiz_obj:
        db_question.quiz = quiz_obj
    db.add(db_question)
    return db_question


def get_question(db: Session, question_id: uuid.UUID) -> Optional[QuizQuestion]:
    return db.get(QuizQuestion, question_id)


def get_questions_for_quiz(db: Session, quiz_id: uuid.UUID) -> Sequence[QuizQuestion]:
    statement = (
        select(QuizQuestion)
        .where(QuizQuestion.quiz_id == quiz_id)
        .order_by(QuizQuestion.order)
    )
    results = db.exec(statement).all()
    return results


def update_question(
    db: Session, *, db_question: QuizQuestion, question_in: QuizQuestionUpdate
) -> QuizQuestion:
    update_data = question_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_question, key, value)
    db.add(db_question)
    return db_question


def delete_question(db: Session, question_id: uuid.UUID) -> Optional[QuizQuestion]:
    db_question = db.get(QuizQuestion, question_id)
    if db_question:
        db.delete(db_question)
    return db_question


def create_user_progress(
    db: Session, *, progress_in: UserProgressCreate
) -> UserProgress:
    existing = get_user_progress_for_item(
        db,
        user_id=progress_in.user_id,
        item_id=progress_in.item_id,
        item_type=progress_in.item_type,
    )
    if existing:
        if not existing.completed_at and progress_in.completed_at:
            existing.completed_at = progress_in.completed_at
            if progress_in.meta_data:
                existing.meta_data = progress_in.meta_data
            db.add(existing)
        return existing
    else:
        db_progress = UserProgress.model_validate(progress_in)
        db.add(db_progress)
        return db_progress


def get_user_progress_for_item(
    db: Session, *, user_id: uuid.UUID, item_id: uuid.UUID, item_type: ItemTypeEnum
) -> Optional[UserProgress]:
    statement = select(UserProgress).where(
        UserProgress.user_id == user_id,
        UserProgress.item_id == item_id,
        UserProgress.item_type == item_type,
    )
    result = db.exec(statement).first()
    return result


def get_user_progress_all(db: Session, *, user_id: uuid.UUID) -> Sequence[UserProgress]:
    statement = (
        select(UserProgress)
        .where(UserProgress.user_id == user_id)
        .order_by(UserProgress.completed_at.desc())
    )
    results = db.exec(statement).all()
    return results


def create_quiz_attempt(
    db: Session,
    *,
    user_id: uuid.UUID,
    attempt_in: UserQuizAttemptCreate,
    score: float,
    passed: bool,
) -> UserQuizAttempt:
    db_attempt = UserQuizAttempt(
        **attempt_in.model_dump(),
        user_id=user_id,
        score=score,
        passed=passed,
        completed_at=datetime.utcnow(),
    )
    db.add(db_attempt)
    return db_attempt


def get_quiz_attempt(db: Session, attempt_id: uuid.UUID) -> Optional[UserQuizAttempt]:
    return db.get(UserQuizAttempt, attempt_id)


def get_user_quiz_attempts(
    db: Session, *, user_id: uuid.UUID, quiz_id: Optional[uuid.UUID] = None
) -> Sequence[UserQuizAttempt]:
    statement = select(UserQuizAttempt).where(UserQuizAttempt.user_id == user_id)
    if quiz_id:
        statement = statement.where(UserQuizAttempt.quiz_id == quiz_id)
    statement = statement.order_by(UserQuizAttempt.completed_at.desc())
    results = db.exec(statement).all()
    return results


def create_assignment_submission(
    db: Session, *, user_id: uuid.UUID, submission_in: UserAssignmentSubmissionCreate
) -> UserAssignmentSubmission:
    db_submission = UserAssignmentSubmission(
        **submission_in.model_dump(),
        user_id=user_id,
    )
    db.add(db_submission)
    return db_submission


def get_assignment_submission(
    db: Session, submission_id: uuid.UUID
) -> Optional[UserAssignmentSubmission]:
    return db.get(UserAssignmentSubmission, submission_id)


def update_assignment_submission(
    db: Session,
    *,
    db_submission: UserAssignmentSubmission,
    update_in: UserAssignmentSubmissionUpdate,
) -> UserAssignmentSubmission:
    update_data = update_in.model_dump(exclude_unset=True)
    needs_update = False
    status_or_grade_changed = False

    for key, value in update_data.items():
        if getattr(db_submission, key) != value:
            setattr(db_submission, key, value)
            needs_update = True
            if key in ["status", "grade"]:
                status_or_grade_changed = True

    if status_or_grade_changed:
        db_submission.graded_at = datetime.utcnow()
        needs_update = True

    if needs_update:
        db.add(db_submission)
    return db_submission


def get_user_assignment_submissions(
    db: Session, *, user_id: uuid.UUID, assignment_id: Optional[uuid.UUID] = None
) -> Sequence[UserAssignmentSubmission]:
    statement = select(UserAssignmentSubmission).where(
        UserAssignmentSubmission.user_id == user_id
    )
    if assignment_id:
        statement = statement.where(
            UserAssignmentSubmission.assignment_id == assignment_id
        )
    statement = statement.order_by(UserAssignmentSubmission.submitted_at.desc())
    results = db.exec(statement).all()
    return results


def delete_assignment_submission(
    db: Session, submission_id: uuid.UUID
) -> Optional[UserAssignmentSubmission]:
    db_submission = db.get(UserAssignmentSubmission, submission_id)
    if db_submission:
        db.delete(db_submission)
    return db_submission
