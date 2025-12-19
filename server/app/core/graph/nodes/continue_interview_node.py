from langgraph.types import interrupt

from app.core.graph.state import InterviewCoachState
from app.core.graph.nodes.base_node import BaseNode
from langchain_core.messages import HumanMessage


class ContinueInterviewNode(BaseNode):
    def __init__(self):
        super().__init__("ContinueInterview")

    def execute(self, state: InterviewCoachState) -> InterviewCoachState:
        self._log_start()

        interruption_interview_question = state.get("intruption_interview_question", "")

        if interruption_interview_question:
            self.logger.info(
                f"Triggering interrupt with question: {interruption_interview_question}"
            )
            # interrupt() pauses execution and returns the resume value
            user_response = interrupt(interruption_interview_question)
            self._log_end(f"Interrupt resolved with answer: {user_response}")

            # Add user's response to messages
            updated_message = HumanMessage(content=user_response)

            return {
                "messages": [updated_message],
            }
        else:
            self._log_end("No interruption needed")

        return state
