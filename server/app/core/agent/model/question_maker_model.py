from pydantic import BaseModel, Field
from typing import List


class Question(BaseModel):
    """
    Question for the interview
    """

    question_number: str = Field(..., description="Question number")
    question: str = Field(..., description="Question for the interview")
    expected_answer: str = Field(..., description="Expected answer for the question")


class QuestionSet(BaseModel):
    """
    Question set for the interview
    """

    questions: List[Question] = Field(
        ..., description="List of questions for the interview"
    )
    total_number_of_questions: int = Field(
        ..., description="Total number of questions for the interview"
    )
