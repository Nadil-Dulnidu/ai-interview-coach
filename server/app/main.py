from fastapi import FastAPI
from app.config.logging import configure_logging, LogLevels
from app.api.router.interview_coach import router as interview_coach_router
from fastapi.middleware.cors import CORSMiddleware

configure_logging(LogLevels.info)

app = FastAPI(
    title="InterviewIQ",
    description="An AI-powered coaching platform designed to help candidates prepare for job interviews through interactive practice and feedback.",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
import os

# ... other imports ...

# Example of loading from environment variable
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
allowed_origins = [origin.strip() for origin in cors_origins_str.split(',') if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(interview_coach_router, prefix="/interview-coach", tags=["Chat"])
