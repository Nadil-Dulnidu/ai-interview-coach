from pydantic import BaseModel, Field
from typing import List


class UserResponse(BaseModel):
    """
    User response for the interview
    """

    question_id: str = Field(..., description="Question id")
    question: str = Field(..., description="Question")
    user_answer: str = Field(..., description="User answer for the question")


class InterviewerModel(BaseModel):
    """
    Interviewer model for the interview
    """

    user_response: List[UserResponse] = Field(..., description="User response")
    current_question: str = Field(
        ..., description="Current question want to ask from candidate"
    )
