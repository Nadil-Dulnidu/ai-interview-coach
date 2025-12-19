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

from app.core.agent.agents import (
    get_req_gathering_agent,
    get_interview_strategist_agent,
    get_interviewer_agent,
    get_question_maker_agent,
)
from app.core.graph.state import InterviewCoachState
from app.core.graph import InterviewCoachGraphBuilder


# Configure logging
logger = logging.getLogger(__name__)


def create_interview_coach_graph(checkpointer=None):
    """
    Factory function to create the interview coach graph.

    This function:
    1. Initializes the requirement gathering agent
    2. Initializes the interview strategist agent
    3. Creates a graph builder with dependencies
    4. Builds and returns the compiled graph

    Args:
        checkpointer: Optional checkpointer for state persistence.
                     Defaults to InMemorySaver if not provided.

    Returns:
        Compiled StateGraph ready for execution.
    """
    logger.info("Creating Interview Coach graph...")

    # Initialize dependencies
    req_gathering_agent = get_req_gathering_agent()
    interview_strategy_agent = get_interview_strategist_agent()
    interviewer_agent = get_interviewer_agent()
    question_maker_agent = get_question_maker_agent()
    checkpointer = checkpointer or InMemorySaver()

    # Build the graph
    builder = InterviewCoachGraphBuilder(
        req_gathering_agent=req_gathering_agent,
        interview_strategy_agent=interview_strategy_agent,
        question_maker_agent=question_maker_agent,
        interviewer_agent=interviewer_agent,
        checkpointer=checkpointer,
    )

    compiled_graph = builder.build()
    logger.info("Interview Coach graph created successfully")

    return compiled_graph


# Global compiled graph instance (for backward compatibility)
compiled_graph = create_interview_coach_graph()


if __name__ == "__main__":
    """
    Interactive example of the interview coach graph.

    This demonstrates how to:
    1. Stream the graph execution in real-time
    2. Handle interrupts and display them to the user
    3. Use LangGraph Command API to resume after interrupts
    4. Loop until the workflow completes
    """
    from langgraph.types import Command

    print("=" * 80)
    print("🤖 AI INTERVIEW COACH - Interactive Demo")
    print("=" * 80)
    print("\nThis demo will guide you through the interview preparation process.")
    print("Answer the questions as they appear, and type 'quit' to exit.\n")

    # Configuration for thread persistence
    config = {"configurable": {"thread_id": "thread-1"}}

    # Initial user message
    user_input = input("👤 What job are you applying for? ")
    if user_input.lower() == "quit":
        print("Exiting...")
        exit(0)

    # Create initial state
    initial_state = InterviewCoachState(
        messages=[HumanMessage(content=user_input)],
        requirements=None,
        requirements_completed=False,
        intruption_question="",
        interview_strategy=None,
    )

    # Track if we're resuming from an interrupt
    is_resuming = False
    resume_input = None

    # Interactive loop
    while True:
        print("\n" + "-" * 80)
        print("🔄 Processing...")
        print("-" * 80)

        # Determine what to invoke
        if is_resuming:
            # Resume from checkpoint and provide the user's answer
            # The value passed to Command(resume=...) is what interrupt() returns
            invoke_input = Command(resume=resume_input)
        else:
            # First run with initial state
            invoke_input = initial_state

        # Stream the graph execution
        try:
            stream = compiled_graph.stream(
                invoke_input, config=config, stream_mode="values"
            )

            interrupt_found = False
            last_state = None

            for chunk in stream:
                # With stream_mode="values", chunk is the complete state
                if chunk is None:
                    continue

                last_state = chunk

                # Check for interrupts in the state
                if isinstance(chunk, dict) and "__interrupt__" in chunk:
                    interrupt_found = True
                    interrupts = chunk["__interrupt__"]

                    print("\n" + "=" * 80)
                    print("⏸️  INTERRUPT DETECTED")
                    print("=" * 80)

                    # Display all interrupt messages
                    for interrupt in interrupts:
                        question = (
                            interrupt.value
                            if hasattr(interrupt, "value")
                            else str(interrupt)
                        )
                        print(f"\n🤔 {question}\n")

                    # Get user response
                    user_response = input("👤 Your answer: ")

                    if user_response.lower() == "quit":
                        print("\n👋 Exiting interview coach. Good luck!")
                        exit(0)

                    # Prepare to resume with Command API
                    is_resuming = True
                    resume_input = user_response
                    break

            # If no interrupt found, check if we're done
            if not interrupt_found:
                print("\n" + "=" * 80)
                print("✅ WORKFLOW COMPLETED!")
                print("=" * 80)

                # Display final results
                if last_state and isinstance(last_state, dict):
                    print("\n📋 Final State:")

                    requirements = last_state.get("requirements")
                    if requirements:
                        print("\n✓ Requirements gathered:")
                        if hasattr(requirements, "model_dump"):
                            import json

                            print(json.dumps(requirements.model_dump(), indent=2))
                        else:
                            print(f"  {requirements}")

                    interview_strategy = last_state.get("interview_strategy")
                    if interview_strategy:
                        print("\n✓ Interview Strategy generated:")
                        import json

                        print(json.dumps(interview_strategy, indent=2))

                    interview_questions = last_state.get("interview_questions")
                    if interview_questions:
                        print("\n✓ Interview Questions generated:")
                        import json

                        print(json.dumps(interview_questions, indent=2))

                    interview_output = last_state.get("interview_output")
                    if interview_output:
                        print("\n✓ Interviewer generated:")
                        import json

                        print(json.dumps(interview_output, indent=2))

                    print("\n🎉 Your interview preparation is complete!")

                break

        except Exception as e:
            print(f"\n❌ Error occurred: {str(e)}")
            import traceback

            traceback.print_exc()
            break

    print("\n" + "=" * 80)
    print("Thank you for using AI Interview Coach!")
    print("=" * 80)
