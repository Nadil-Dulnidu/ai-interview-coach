from pydantic import BaseModel, Field
import enum
from typing import List, Optional


class InterviewPreference(BaseModel):
    """Interview preference."""

    experience_level: List[str] = Field(
        ..., description="Experience level of the candidate"
    )
    job_role: str = Field(
        ..., description="Job role of the candidate would like to apply"
    )
    tech_stack: List[str] = Field(..., description="Technical stack of the candidate")
    interview_type: str = Field(..., description="Type of interview")
    focus_area: List[str] = Field(..., description="Focus area of the interview")


class UserConfirmations(BaseModel):
    """User confirmations."""

    notes: Optional[str] = Field(None, description="Additional candidate notes")


class MissingInfo(BaseModel):
    """Missing information."""

    missing_info: List[str] = Field(
        ..., description="List of missing or ambiguous fields"
    )
    question: str = Field(
        ..., description="Question to ask the user to provide the missing information"
    )


class ReqGathringModel(BaseModel):
    """Request gathering model."""

    interview_preference: InterviewPreference = Field(
        ..., description="Interview preference"
    )
    user_confirmations: UserConfirmations = Field(..., description="User confirmations")
    missing_info: MissingInfo = Field(..., description="Missing information")
