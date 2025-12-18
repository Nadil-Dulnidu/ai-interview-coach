from fastapi import FastAPI
from app.config.logging import configure_logging, LogLevels

configure_logging(LogLevels.info)

app = FastAPI(
    title="AI Interview Coach", version="0.0.1", description="AI Interview Coach API"
)
