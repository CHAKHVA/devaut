from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import quiz_endpoints
from app.core.config import settings

app = FastAPI(
    title="JD Quiz Generator API",
    version="0.1.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

origins = [
    "http://localhost:3000",
    # "https://your-frontend-domain.com",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quiz_endpoints.router, prefix=settings.API_V1_STR, tags=["Quiz App"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the JD Quiz Generator API"}
