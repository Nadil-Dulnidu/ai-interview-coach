from app.core.graph.nodes.base_node import BaseNode
from app.exceptions.graph_exceptions import AgentInvocationError
from app.core.graph.state import InterviewCoachState
from langchain.messages import HumanMessage

from typing import Any, Dict

from tenacity import retry, stop_after_attempt, wait_exponential


class InterviewStrategyNode(BaseNode):
    """
    This node is responsible for generating the interview strategy.

    Attributes:
        agent (Agent): The agent to use for generating the interview strategy.
    """

    def __init__(self, agent):
        self.agent = agent

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def execute(self, state: InterviewCoachState) -> InterviewCoachState:

        self._log_start()

        try:

            requirements = state["requirements"]

            messages = HumanMessage(
                content="Here are the requirements: " + requirements.model_dump_json()
            )

            response = self.agent.invoke({"messages": [messages]})

            if not response:
                self.logger.error("Empty response from agent")
                raise AgentInvocationError("Empty response from agent")

            structured_response = response["structured_response"]

            result = {
                "messages": state["messages"],
                "interview_strategy": structured_response.model_dump(),
                "requirements": state["requirements"],
                "requirements_completed": state["requirements_completed"],
                "intruption_question": state["intruption_question"],
            }

            self._log_end("Interview strategy generated successfully")
            return result

        except Exception as e:
            self._log_error(e)
            # Return safe error state to allow graceful recovery
            return self._create_safe_error_state(state)
