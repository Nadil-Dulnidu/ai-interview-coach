from pydantic import BaseModel, Field
from typing import List


class QuestionEvaluation(BaseModel):
    """
    Evaluation result for a single interview question
    """

    question_id: str = Field(..., description="Question id")
    question: str = Field(..., description="Interview question")
    user_answer: str = Field(..., description="User's answer")
    expected_answer: str = Field(..., description="Expected answer reference")

    score: float = Field(
        ...,
        ge=0,
        le=10,
        description="Score for this answer (0–10)",
    )

    strengths: List[str] = Field(
        ..., description="What the candidate did well in this answer"
    )

    weaknesses: List[str] = Field(
        ..., description="What was missing or incorrect in this answer"
    )

    improvement_suggestions: List[str] = Field(
        ..., description="Concrete suggestions to improve this answer"
    )


class InterviewEvaluation(BaseModel):
    """
    Overall evaluation for the interview
    """

    question_evaluations: List[QuestionEvaluation] = Field(
        ..., description="Evaluation for each interview question"
    )

    average_score: float = Field(
        ..., ge=0, le=10, description="Average score across all questions"
    )

    overall_strengths: List[str] = Field(
        ..., description="High-level strengths observed across the interview"
    )

    overall_weaknesses: List[str] = Field(
        ..., description="High-level weaknesses observed across the interview"
    )

    hire_recommendation: str = Field(
        ...,
        description="Overall recommendation: Strong Hire | Hire | No Hire | Strong No Hire",
    )
