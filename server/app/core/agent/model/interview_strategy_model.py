from pydantic import BaseModel, Field
import enum
from typing import List


class InterviewDifficultyLevel(str, enum.Enum):
    """Interview difficulty level."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class InterviewTypeDistribution(BaseModel):
    """Interview type distribution."""

    technical: int = Field(..., description="Number of technical interview questions")
    behavioral: int = Field(..., description="Number of behavioral interview questions")


class Topic(BaseModel):
    """Topic model."""

    name: str = Field(..., description="Topic name")
    questions: int = Field(..., description="Number of questions")
    focus: str = Field(..., description="Focus of the topic")


class InterviewStrategy(BaseModel):
    """Interview strategy."""

    difficulty: InterviewDifficultyLevel = Field(
        ..., description="Interview difficulty level"
    )
    interview_type_distribution: InterviewTypeDistribution = Field(
        ..., description="Interview type distribution"
    )
    topics: List[Topic] = Field(..., description="List of topics")
    total_questions: int = Field(..., description="Number of all questions")
