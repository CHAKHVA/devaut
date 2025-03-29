# from app.api.v1.api import api_router as api_router_v1
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Personalized Learning Platform API",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
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


# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Learning Platform API. See /api/v1/docs for documentation."
    }


# app.include_router(api_router_v1, prefix="/api/v1")
