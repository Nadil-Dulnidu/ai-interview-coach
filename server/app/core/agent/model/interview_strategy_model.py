from pydantic import BaseModel, Field
import enum
from typing import List


class QuestionDifficultyLevel(str, enum.Enum):
    """Question difficulty level."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Question(BaseModel):
    """Question."""

    question: str = Field(..., description="Interview question")
    answer: str = Field(..., description="Answer for the interview question")
    question_difficulty_level: QuestionDifficultyLevel = Field(
        ..., description="Question Difficulty level"
    )


class InterviewStrategy(BaseModel):
    """Interview strategy."""

    questions: List[Question] = Field(..., description="List of questions")
    number_of_questions: int = Field(..., description="Number of all questions")
