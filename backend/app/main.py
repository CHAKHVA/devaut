# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your API routers later when you create them
# from app.api.v1 import api_router as api_v1_router

app = FastAPI(title="Personalized Learning Platform API", version="0.1.0")

# CORS Middleware (adjust origins as needed for your frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "your-frontend-domain.com",
    ],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Learning Platform API"}


# Include your API routers here later
# app.include_router(api_v1_router, prefix="/api/v1")

# Add other startup/shutdown events if necessary
