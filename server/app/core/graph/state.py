from langgraph.graph import MessagesState
from app.core.agent.model.req_gathring_model import ReqGathringModel
from app.core.agent.model.interviewer_model import InterviewerModel
from app.core.agent.model.interview_strategy_model import InterviewStrategy
from app.core.agent.model.question_maker_model import QuestionSet
from app.core.agent.model.evalutaion_model import InterviewEvaluation
from app.core.agent.model.dynamic_prompt_model import Context


class InterviewCoachState(MessagesState):
    """
    This class is responsible for storing the state of the interview coach application.

    Attributes:
        requirements (ReqGathringModel | None): The requirements of the candidate.
        requirements_completed (bool): Whether the requirements have been completed.
        intruption_question (str): The question that was interrupted.
        interview_strategy (InterviewStrategy | None): The interview strategy.
        interview_questions (QuestionSet | None): The interview questions.
        interview_output (InterviewerModel | None): The interview output.
        is_interview_completed (bool): Whether the interview has been completed.
        intruption_interview_question (str): The question that was interrupted.
        final_interview_evaluation (InterviewEvaluation | None): The final interview evaluation.
        final_user_requirements (ReqGathringModel | None): The final user requirements.
    """

    requirements: ReqGathringModel | None = None
    requirements_completed: bool = False
    intruption_question: str = ""

    interview_strategy: InterviewStrategy | None = None

    interview_questions: QuestionSet | None = None

    interview_output: InterviewerModel | None = None
    is_interview_completed: bool = False
    intruption_interview_question: str = ""

    final_interview_evaluation: InterviewEvaluation | None = None

    final_user_requirements: ReqGathringModel | None = None

    context: Context | None = None
