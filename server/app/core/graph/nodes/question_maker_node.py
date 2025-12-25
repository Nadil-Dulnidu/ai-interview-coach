from app.core.graph.nodes.base_node import BaseNode
from app.exceptions.graph_exceptions import AgentInvocationError
from app.core.graph.state import InterviewCoachState
from langchain_core.messages import HumanMessage, AIMessage

from typing import Any, Dict

from tenacity import retry, stop_after_attempt, wait_exponential


class QuestionMakerNode(BaseNode):
    """
    Question maker node
    """

    def __init__(self, agent: Any):
        super().__init__("QuestionMakerNode")
        self.agent = agent

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def execute(self, state: InterviewCoachState) -> InterviewCoachState:
        self._log_start()

        try:

            user_requirements = state["requirements"]
            interview_strategy = state["interview_strategy"]

            messages = HumanMessage(
                content=f"Here are the user requirements: {user_requirements}. Here is the interview strategy: {interview_strategy}"
            )

            response = self.agent.invoke({"messages": [messages]})

            if not response:
                self.logger.error("Empty response from agent")
                raise AgentInvocationError("Empty response from agent")

            structured_response = response["structured_response"]

            result = {
                "messages": [
                    AIMessage(
                        content="I have analyzed the requirements and strategy to generate a tailored set of interview questions. I'm ready to begin the interview when you are.\n\n"
                    )
                ],
                "interview_questions": structured_response.model_dump(),
            }

            self._log_end("Interview questions generated successfully")
            return result

        except Exception as e:
            self._log_error(e)
            # Return safe error state to allow graceful recovery
            return self._create_safe_error_state(state)
