import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.crud import quiz_crud
from app.db.session import get_db
from app.schemas import quiz_schemas
from app.services import quiz_services

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/generate-quiz/",
    response_model=quiz_schemas.GenerateQuizResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Quiz from Job Description",
    description="Submits a job description, generates a quiz using AI, saves both, and returns the job description details including minimal info about the generated quiz.",
    tags=["Quiz Generation & Matching"],
)
async def generate_quiz_from_jd(
    *,
    db: Session = Depends(get_db),
    request_data: quiz_schemas.GenerateQuizRequest,
):
    logger.info(
        f"Received request to generate quiz for job description starting with: {request_data.job_description_text[:100]}..."
    )
    try:
        created_jd_read = await quiz_services.generate_quiz_for_jd(
            db=db, jd_text=request_data.job_description_text
        )
        return quiz_schemas.GenerateQuizResponse(job_description=created_jd_read)

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error during quiz generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during quiz generation.",
        )


@router.post(
    "/match-quiz/",
    response_model=quiz_schemas.MatchQuizResponse,
    summary="Match Existing Quizzes",
    description="Finds existing quizzes that match either tags extracted from provided job description text or a provided list of tags.",
    tags=["Quiz Generation & Matching"],
)
async def match_existing_quizzes(
    *,
    db: Session = Depends(get_db),
    request_data: quiz_schemas.MatchQuizRequest,
):
    if not request_data.job_description_text and not request_data.tags:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'job_description_text' or 'tags' must be provided for matching.",
        )

    logger.info(
        f"Received request to match quizzes. JD provided: {bool(request_data.job_description_text)}, Tags provided: {request_data.tags}"
    )
    try:
        matched_quizzes_info = await quiz_services.find_matching_quizzes(
            db=db,
            jd_text=request_data.job_description_text,
            tags=request_data.tags,
        )
        return quiz_schemas.MatchQuizResponse(matched_quizzes=matched_quizzes_info)

    except HTTPException as http_exc:
        raise http_exc
    except NotImplementedError as nie:
        logger.error(f"Feature not implemented: {nie}")
        raise HTTPException(status_code=501, detail=str(nie))
    except Exception as e:
        logger.error(f"Unexpected error during quiz matching: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during quiz matching.",
        )


@router.get(
    "/job-descriptions/",
    response_model=List[quiz_schemas.JobDescriptionRead],
    summary="List Job Descriptions",
    description="Retrieves a list of job descriptions with pagination.",
    tags=["Job Descriptions"],
)
def read_job_descriptions(
    *,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(
        100, ge=1, le=200, description="Maximum number of items to return"
    ),
):
    jds = quiz_crud.get_job_descriptions(db=db, skip=skip, limit=limit)
    return jds


@router.get(
    "/job-descriptions/{jd_id}",
    response_model=quiz_schemas.JobDescriptionRead,
    summary="Get Job Description by ID",
    description="Retrieves details of a specific job description, including minimal info about its generated quiz if available.",
    tags=["Job Descriptions"],
)
def read_job_description(
    *,
    db: Session = Depends(get_db),
    jd_id: int,
):
    db_jd = quiz_crud.get_job_description(db=db, jd_id=jd_id)
    if db_jd is None:
        logger.warning(f"Job Description with ID {jd_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job Description with ID {jd_id} not found",
        )
    # db.refresh(db_jd, attribute_names=['generated_quiz']) # Might be needed depending on lazy loading config
    return db_jd


@router.get(
    "/quizzes/",
    response_model=List[quiz_schemas.QuizRead],
    summary="List Quizzes",
    description="Retrieves a list of quizzes with pagination, including their questions.",
    tags=["Quizzes"],
)
def read_quizzes(
    *,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(
        100, ge=1, le=200, description="Maximum number of items to return"
    ),
):
    quizzes = quiz_crud.get_quizzes(db=db, skip=skip, limit=limit)
    return quizzes


@router.get(
    "/quizzes/{quiz_id}",
    response_model=quiz_schemas.QuizRead,
    summary="Get Quiz by ID",
    description="Retrieves details of a specific quiz, including its questions and answers.",
    tags=["Quizzes"],
)
def read_quiz(
    *,
    db: Session = Depends(get_db),
    quiz_id: int,
):
    db_quiz = quiz_crud.get_quiz(db=db, quiz_id=quiz_id)
    if db_quiz is None:
        logger.warning(f"Quiz with ID {quiz_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz with ID {quiz_id} not found",
        )
    # db.refresh(db_quiz, attribute_names=['questions'])
    return db_quiz
