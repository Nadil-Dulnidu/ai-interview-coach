from langgraph.graph import MessagesState
from app.core.agent.model.req_gathring_model import ReqGathringModel
from app.core.agent.model.interviewer_model import InterviewerModel
from app.core.agent.model.interview_strategy_model import InterviewStrategy


class InterviewCoachState(MessagesState):
    """
    This class is responsible for storing the state of the interview coach application.

    Attributes:
        requirements (ReqGathringModel | None): The requirements of the candidate.
        requirements_completed (bool): Whether the requirements have been completed.
        intruption_question (str): The question that was interrupted.
        interview_strategy (InterviewStrategy | None): The interview strategy.
        interview_context (InterviewerModel | None): The interview context.
        is_interview_completed (bool): Whether the interview has been completed.
        intruption_interview_question (str): The question that was interrupted.
    """

    requirements: ReqGathringModel | None = None
    requirements_completed: bool = False
    intruption_question: str = ""
    interview_strategy: InterviewStrategy | None = None
    interview_context: InterviewerModel | None = None
    is_interview_completed: bool = False
    intruption_interview_question: str = ""
