from fastapi import FastAPI
from app.config.logging import configure_logging, LogLevels
from app.api.router.interview_coach import router as interview_coach_router
from fastapi.middleware.cors import CORSMiddleware

configure_logging(LogLevels.debug)

app = FastAPI(
    title="AI Interview Coach",
    description="An AI-powered coaching platform designed to help candidates prepare for job interviews through interactive practice and feedback.",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(
    interview_coach_router, prefix="/interview-coach", tags=["Interview Coach"]
)
