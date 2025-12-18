"""
Interview Coach Graph - Main Entry Point.

This module provides the compiled graph instance for the AI Interview Coach
workflow. It uses the refactored architecture with separate node classes
and a graph builder for better maintainability and testability.

The graph orchestrates the requirement gathering process with support for
interruptions and follow-up questions.
"""

import logging

from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage

from app.core.agent.agents import get_req_gathering_agent
from app.core.graph.state import InterviewCoachState
from app.core.graph import InterviewCoachGraphBuilder


# Configure logging
logger = logging.getLogger(__name__)


def create_interview_coach_graph(checkpointer=None):
    """
    Factory function to create the interview coach graph.

    This function:
    1. Initializes the requirement gathering agent
    2. Creates a graph builder with dependencies
    3. Builds and returns the compiled graph

    Args:
        checkpointer: Optional checkpointer for state persistence.
                     Defaults to InMemorySaver if not provided.

    Returns:
        Compiled StateGraph ready for execution.
    """
    logger.info("Creating Interview Coach graph...")

    # Initialize dependencies
    req_gathering_agent = get_req_gathering_agent()
    checkpointer = checkpointer or InMemorySaver()

    # Build the graph
    builder = InterviewCoachGraphBuilder(
        req_gathering_agent=req_gathering_agent, checkpointer=checkpointer
    )

    compiled_graph = builder.build()
    logger.info("Interview Coach graph created successfully")

    return compiled_graph


# Global compiled graph instance (for backward compatibility)
compiled_graph = create_interview_coach_graph()


if __name__ == "__main__":
    """
    Example usage of the interview coach graph.

    This demonstrates how to:
    1. Configure the graph with a thread ID for conversation persistence
    2. Initialize the state with a user message
    3. Invoke the graph and get the response
    """
    config = {"configurable": {"thread_id": "thread-1"}}

    initial_state = InterviewCoachState(
        messages=[
            HumanMessage(content="I want to apply for a job as a software engineer")
        ],
        requirements=None,
        requirements_completed=False,
        intruption_question="",
        interview_strategy=None,
    )

    response = compiled_graph.stream(initial_state, config=config)
    for chunk in response:
        if "__intterupt__" in chunk:
            print(chunk["__intterupt__"])
        else:
            print(chunk)
