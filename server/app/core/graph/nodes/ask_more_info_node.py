"""
Interruption node for asking follow-up questions.

This module contains the node responsible for interrupting the workflow
when additional information is needed from the candidate.
"""

from langgraph.types import interrupt

from app.core.graph.state import InterviewCoachState
from app.core.graph.nodes.base_node import BaseNode
from langchain_core.messages import HumanMessage


class AskMoreInfoNode(BaseNode):
    """
    Node responsible for interrupting the workflow to ask follow-up questions.

    This node checks if there's an interruption question in the state and,
    if so, triggers a LangGraph interrupt to pause execution and wait for
    user input.
    """

    def __init__(self):
        """Initialize the ask more info node."""
        super().__init__("AskMoreInfo")

    def execute(self, state: InterviewCoachState) -> InterviewCoachState:
        """
        Execute the interruption logic.

        This method checks if there's an interruption question and triggers
        a LangGraph interrupt to pause the workflow for user input.
        When resumed, it appends the user's response to the messages.

        Args:
            state: Current state containing the interruption question.

        Returns:
            Updated state with user's response added to messages.
        """
        self._log_start()

        interruption_question = state.get("intruption_question", "")

        if interruption_question:
            self.logger.info(
                f"Triggering interrupt with question: {interruption_question}"
            )
            # interrupt() pauses execution and returns the resume value
            user_response = interrupt(interruption_question)
            self._log_end(f"Interrupt resolved with answer: {user_response}")

            return {
                "messages": [HumanMessage(content=user_response)],
                "intruption_question": "",  # Clear the interrupt question
            }
        else:
            self._log_end("No interruption needed")

        return state
