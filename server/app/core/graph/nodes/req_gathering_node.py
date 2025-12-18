"""
Requirement gathering node for the interview coach workflow.

This module contains the node responsible for collecting candidate requirements
such as job title, company, experience level, and other relevant information
needed to conduct an effective mock interview.
"""

from typing import Any, Dict

from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.graph.state import InterviewCoachState
from app.core.graph.nodes.base_node import BaseNode
from app.exceptions.graph_exceptions import AgentInvocationError


class RequirementGatheringNode(BaseNode):
    """
    Node responsible for gathering candidate requirements.

    This node interacts with the requirement gathering agent to collect
    necessary information from the candidate. If information is missing,
    it sets up an interruption to ask follow-up questions.

    Attributes:
        agent: The LangChain agent configured for requirement gathering.
    """

    def __init__(self, agent):
        """
        Initialize the requirement gathering node.

        Args:
            agent: The LangChain agent for requirement gathering.
        """
        super().__init__("RequirementGathering")
        self.agent = agent

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def execute(self, state: InterviewCoachState) -> InterviewCoachState:
        """
        Execute the requirement gathering logic.

        This method:
        1. Invokes the requirement gathering agent with current messages
        2. Checks if the response is valid
        3. Determines if more information is needed
        4. Returns updated state with requirements or follow-up question

        Args:
            state: Current state containing conversation messages.

        Returns:
            Updated state with requirements or interruption question.
        """
        self._log_start()

        try:
            messages = state["messages"]
            response = self.agent.invoke({"messages": messages})

            if not response:
                self.logger.error("Empty response from agent")
                raise AgentInvocationError("Empty response from agent")

            structured_response = response["structured_response"]

            # Check if we need more information
            if structured_response.missing_info.question != "":
                result = self._create_missing_info_state(state, structured_response)
                self._log_end("Missing info - asking follow-up question")
                return result

            # All requirements gathered successfully
            result = self._create_complete_state(state, structured_response)
            self._log_end("Requirements gathered successfully")
            return result

        except Exception as e:
            self._log_error(e)
            # Return safe error state to allow graceful recovery
            return self._create_safe_error_state(state)

    def _create_missing_info_state(
        self, state: InterviewCoachState, structured_response: Any
    ) -> Dict[str, Any]:
        """
        Create state when missing information is detected.

        Args:
            state: Current state.
            structured_response: The agent's structured response.

        Returns:
            State with interruption question set.
        """
        return {
            "messages": state["messages"],
            "requirements": None,
            "requirements_completed": False,
            "intruption_question": structured_response.missing_info.question,
        }

    def _create_complete_state(
        self, state: InterviewCoachState, structured_response: Any
    ) -> Dict[str, Any]:
        """
        Create state when all requirements are gathered.

        Args:
            state: Current state.
            structured_response: The agent's structured response.

        Returns:
            State with complete requirements.
        """
        return {
            "messages": state["messages"],
            "requirements": structured_response.model_dump(),
            "requirements_completed": True,
            "intruption_question": "",
        }
