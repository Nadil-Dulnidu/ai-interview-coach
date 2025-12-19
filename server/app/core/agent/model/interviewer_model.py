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

    is_candidate_ready: bool = Field(
        ..., description="Is the candidate ready to face the interview"
    )

    user_responses: List[UserResponse] = Field(
        ..., description="User responses for each question"
    )

    missing_user_answer_questions: List[str] = Field(
        ...,
        description="The questions that the user has not answered yet",
    )
    question: str = Field(
        ...,
        description="The question that requires a response from the user",
    )
