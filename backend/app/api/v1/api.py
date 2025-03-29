# app/api/v1/api.py
# Import endpoint routers specific to API version 1
from app.api.v1.endpoints import auth, gamification, progress, roadmaps, users
from fastapi import APIRouter

# Create the main router for API version 1
api_router = APIRouter()

# Include individual endpoint routers, organizing them with prefixes and tags
# Tags are used for grouping endpoints in the OpenAPI documentation (Swagger UI/ReDoc).
# Prefixes define the base path for all routes within the included router.
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users & Profile"])
api_router.include_router(
    roadmaps.router, prefix="/roadmaps", tags=["Roadmaps & Content"]
)
api_router.include_router(
    progress.router, prefix="/progress", tags=["User Progress & Submissions"]
)
api_router.include_router(
    gamification.router, prefix="/gamification", tags=["Gamification & Leaderboard"]
)

# You could add common dependencies, responses, or middleware specific to v1 here
# using `dependencies=[...` or `responses={...}` arguments in APIRouter or include_router
# if needed, but generally keep endpoint-specific logic within the endpoint files.
