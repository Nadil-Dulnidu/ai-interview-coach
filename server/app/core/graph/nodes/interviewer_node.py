from app.core.graph.nodes.base_node import BaseNode
from app.exceptions.graph_exceptions import AgentInvocationError
from app.core.graph.state import InterviewCoachState
from langchain_core.messages import HumanMessage

from typing import Any, Dict

from tenacity import retry, stop_after_attempt, wait_exponential


class InterviewerNode(BaseNode):

    def __init__(self, agent):
        super().__init__("Interviewer")
        self.agent = agent

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def execute(self, state: InterviewCoachState) -> InterviewCoachState:
        self._log_start()

        try:
            interview_questions = state["interview_questions"]

            messages = [
                HumanMessage(
                    content=f"Here are the interview questions: {interview_questions}"
                )
            ] + state["messages"]

            response = self.agent.invoke({"messages": messages})

            print(f"=====Interviewer Agent response========: {response["messages"]}")

            if not response:
                self.logger.error("Empty response from agent")
                raise AgentInvocationError("Empty response from agent")

            structured_response = response["structured_response"]

            print(
                f"=====Interviewer Agent structured response========: {structured_response}"
            )

            # Check if we need more information
            if (
                structured_response.question != ""
                and structured_response.missing_user_answer_questions != []
            ):
                result = self._create_incomplete_state(state, structured_response)
                self._log_end("askinging current question")
                return result

            # All requirements gathered successfully
            result = self._create_complete_state(state, structured_response)
            self._log_end("All questions asked successfully")
            return result

        except Exception as e:
            self._log_error(e)
            # Return safe error state to allow graceful recovery
            return self._create_safe_error_state(state)

    def _create_incomplete_state(
        self, state: InterviewCoachState, structured_response: Any
    ) -> Dict[str, Any]:
        return {
            "is_interview_completed": False,
            "intruption_interview_question": structured_response.question,
        }

    def _create_complete_state(
        self, state: InterviewCoachState, structured_response: Any
    ) -> Dict[str, Any]:
        return {
            "interview_output": structured_response.model_dump(),
            "is_interview_completed": True,
            "intruption_interview_question": "",
        }
