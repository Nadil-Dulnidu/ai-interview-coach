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
            user_response = interrupt(f"\n\n{interruption_interview_question}")
            self._log_end(f"Interrupt resolved with answer: {user_response}")

            # Add the user's response to messages so the interviewer can process it
            return {
                "messages": [HumanMessage(content=user_response)],
                "intruption_interview_question": "",
            }
        else:
            self._log_end("No interruption needed")

        return state
