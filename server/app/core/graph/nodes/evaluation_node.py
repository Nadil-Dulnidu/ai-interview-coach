from app.core.graph.state import InterviewCoachState
from app.core.graph.nodes.base_node import BaseNode
from langchain_core.messages import HumanMessage, AIMessage
from app.exceptions.graph_exceptions import AgentInvocationError
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential


class EvaluationNode(BaseNode):
    def __init__(self, agent: Any):
        super().__init__("EvaluationNode")
        self.agent = agent

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def execute(self, state: InterviewCoachState) -> InterviewCoachState:

        self._log_start()

        try:
            user_requirements = state["requirements"]
            interview_output = state["interview_output"]

            messages = HumanMessage(
                content=f"Here are the user requirements (user profile): {user_requirements}. Here is the interview output: {interview_output}"
            )

            response = self.agent.invoke({"messages": [messages]})

            if not response:
                self.logger.error("Empty response from agent")
                raise AgentInvocationError("Empty response from agent")

            structured_response = response["structured_response"]

            result = {
                "messages": [
                    AIMessage(
                        content="\n\nI have completed the evaluation of the interview output based on the provided requirements. The assessment includes a detailed analysis of the performance, highlighting key strengths and areas for improvement. Have a nice day.\n\n",
                        name="interview_evaluation",
                    )
                ],
                "final_user_requirements": state["requirements"],
                "final_interview_evaluation": structured_response.model_dump(),
            }

            self._log_end("Interview evaluation generated successfully")
            return result

        except Exception as e:
            self._log_error(e)
            # Return safe error state to allow graceful recovery
            return self._create_safe_error_state(state)
