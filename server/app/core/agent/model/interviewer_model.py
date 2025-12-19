from pydantic import BaseModel, Field
from typing import List


class Context(BaseModel):
    """
    Context for the interview
    """

    question: str = Field(..., description="Question for the interview")
    expected_answer: str = Field(..., description="Expected answer for the question")
    user_answer: str = Field(..., description="User answer for the question")


class Progress(BaseModel):
    """
    Progress for the interview
    """

    current_question: str = Field(
        ..., description="Current question want to ask from candidate"
    )
    total_number_of_questions: int = Field(
        ..., description="Total number of questions want to ask from candidate"
    )


class InterviewerModel(BaseModel):
    """
    Interviewer model for the interview
    """

    context: List[Context] = Field(..., description="Context for the interview")
    progress: Progress = Field(..., description="Progress for the interview")
